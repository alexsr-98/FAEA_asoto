# -*- coding: utf-8 -*-
#Para leer el comando con las instrucciones
import numpy as np
from Selector import Selector
from Plotter import Plotter
import ROOT as r
import subprocess
import copy

r.gStyle.SetOptStat(0)
r.gROOT.SetBatch(1)

def read_mca(mca='' , data = 'True', folder = './PruebaMcPlots', selection = []):
  if mca == '':
    print('No has especificado el archivo de montecarlo. \n')
  else:
    lectura = np.loadtxt(mca, dtype='str' ,delimiter = ':')
    lectura = np.char.strip(lectura) #elimina los espacios que hay en el txt
    MCsamples = lectura[1:,1] #asigna las muestras y colores
    colors = []
    for i in lectura[1:,2]:
      colors.append(int(i))
		
    if data == 'True': #para el caso que haya datos
      plot = Plotter(MCsamples, 'data', folder, selection)
      plot.SetColors(colors)
      return plot
			
    else:  #para el caso que no haya datos
      plot = Plotter(MCsamples, '',  folder, selection)
      plot.SetColors(colors)
      return plot
		

def drawer(options=''):
  '''
  El comando tiene esta estructura:
    -[0]: mca
    -[1]: data (true o false)
    -[2]: carpeta donde guardar los plots
    -[3]: plots a dibujar
  '''
  #subprocess.call("./script.sh", shell=True)
  
  comando = np.loadtxt('command.txt', dtype=('str') , delimiter = '--', comments='&') #Comentarios senalados por &
  comando = np.char.strip(comando)
  
  #-----Cortes------
  cortes = comando[5]
  cortes = np.char.strip(cortes.split(','))
  cortes_val = []
  for i in range(0,len(cortes)):
    M = np.char.strip(cortes[i].split('='))
    cortes_val.append(float(M[1]))
  #-----Cortes------
  
  plot = read_mca(mca = comando[0], data = comando[1], folder = comando[2], selection = cortes_val)
  graficas = comando[3]
  titulos_graficas = comando[4]
  titulos_graficas = np.char.strip(titulos_graficas.split(','))
  #---Seleccion de graficas a pintar---
  contador = 0
  for i in np.char.strip(graficas.split(',')):
    plot.SetXtitle(titulos_graficas[contador])
    plot.SetYtitle('Events')
    plot.SetTitle(' ')
    if i == 'NJet' or i == 'NJets_NBJets' or i == 'NBJets':
        plot.SetYaxislog()
    plot.Stack(i)
    contador += 1
  #---Seleccion de graficas a pintar---
  eff_trigg = plot.Trigger_Eff("MuonPt", "MuonPt_notrigg","MuonPt_forEff","MuonPt_notrigg_forEff")
  print('La eficiencia de trigger para pt > %3d GeV: %3.3f +- %3.3f' %(cortes_val[0],eff_trigg,(1-eff_trigg)/2))
  #---Calculo xsection----------
  muestras,eventos = plot.GetCounts("EventWeight")
  
  contador = 0
  fondo = 0
  for nombre in muestras:
    if nombre == 'ttbar':
      ttbar = eventos[contador]
    elif nombre == 'data':
      datos = eventos[contador]
    else: 
      fondo += eventos[contador]
    contador += 1
  
  stat_fondo = (fondo)**(0.5)
  stat_datos = (datos)**(0.5)
  
  Lumi = 50
  unc_Lumi = 0.1
  BR = 0.09732*2

  Acceptance, unc_Acceptance = plot.calc_aceptancia("EventWeight_gen","EventWeight_gen_tot",BR)
  
  eff_muons = 0.99
  #eff_btag = 0.8
  unc_eff_muons = 0.01/0.99
  #unc_eff_btag = 0.1
  unc_eff_trigg = (1-eff_trigg)/2
  eff_btag, unc_eff_btag = plot.calc_btag_eff("NBJets_correcto","NBJets")
  eff_tot = eff_trigg*eff_muons*eff_btag
  print('La eficiencia de btag es: %3.3f +- %3.3f' %(eff_btag,unc_eff_btag))
  eficiencias = np.array([eff_muons,eff_btag,eff_trigg])
  unc_eficiencias = np.array([unc_eff_muons,unc_eff_btag,unc_eff_trigg])
  
  xsection = (datos-fondo)/(BR*Lumi*Acceptance*eff_tot)
  
  #-------Incertidumbres sistemáticas--------
  lectura2 = np.loadtxt('syst_unc.txt', dtype='str' ,delimiter = ':')
  lectura2 = np.char.strip(lectura2) #elimina los espacios que hay en el txt
  MCmuestras = lectura2[:,1]
  MCUnc = lectura2[:,2]
  
  contador1 = 0
  
  nombres_sistematicos = []
  delta_xsection_up = []
  delta_xsection_down = []
  for name in MCmuestras: #propagación incertidumbre en normalización muestras MC
    contador2 = 0
    nombres_sistematicos.append(name)
    for name2 in muestras:
      if name == name2:
        fondo_up = fondo + eventos[contador2]*float(MCUnc[contador1])
        fondo_down = fondo - eventos[contador2]*float(MCUnc[contador1])
        xsection_up = (datos-fondo_up)/(BR*Lumi*Acceptance*eff_tot)
        xsection_down = (datos-fondo_down)/(BR*Lumi*Acceptance*eff_tot)
        delta_xsection_up.append(abs(xsection-xsection_up))  #la diferencia entre el valor nominal y la variación me da la incertidumbre asociada a ese sistemático sobre la xsection
        delta_xsection_down.append(abs(xsection-xsection_down))            
      contador2 +=1
    contador1 += 1    
  
  nombres_sistematicos.append('reco_muones')
  nombres_sistematicos.append('b-tag')
  nombres_sistematicos.append('trigger')
  for i in range(0,len(eficiencias)): #Propagación incertidumbre en eficiencias
    xsection_eff_up = (datos-fondo)/(BR*Lumi*Acceptance*((eff_tot*(eficiencias[i]+eficiencias[i]*unc_eficiencias[i]))/eficiencias[i]))
    xsection_eff_down = (datos-fondo)/(BR*Lumi*Acceptance*((eff_tot*(eficiencias[i]-eficiencias[i]*unc_eficiencias[i]))/eficiencias[i]))
    delta_xsection_up.append(abs(xsection-xsection_eff_up))  
    delta_xsection_down.append(abs(xsection-xsection_eff_down))
  
  nombres_sistematicos.append('aceptancia')
  delta_xsection_up.append(abs(xsection-((datos-fondo)/(BR*Lumi*(Acceptance+unc_Acceptance)*eff_tot))))  #Propagación incertidumbre aceptancia
  delta_xsection_down.append(abs(xsection-((datos-fondo)/(BR*Lumi*(Acceptance-unc_Acceptance)*eff_tot))))
  
  delta_xsection_lumi_up = abs(xsection-((datos-fondo)/(BR*(Lumi+Lumi*unc_Lumi)*Acceptance*eff_tot)))
  delta_xsection_lumi_down = abs(xsection-((datos-fondo)/(BR*(Lumi-Lumi*unc_Lumi)*Acceptance*eff_tot)))
    
  delta_xsection_up_sys = np.sqrt(np.dot(np.array(delta_xsection_up),np.array(delta_xsection_up)))
  delta_xsection_down_sys = np.sqrt(np.dot(np.array(delta_xsection_down),np.array(delta_xsection_down)))
  
    
  #-------Incertidumbres sistemáticas--------
  #-------Incertidumbres estadísticas--------
  delta_xsection_stat_up = []
  delta_xsection_stat_down = []
  
  delta_xsection_stat_up.append(abs(xsection-((datos+stat_datos-fondo)/(BR*Lumi*Acceptance*eff_tot))))
  delta_xsection_stat_up.append(abs(xsection-((datos-fondo-stat_fondo)/(BR*Lumi*Acceptance*eff_tot))))
  delta_xsection_stat_down.append(abs(xsection-((datos-stat_datos-fondo)/(BR*Lumi*Acceptance*eff_tot))))
  delta_xsection_stat_down.append(abs(xsection-((datos-fondo+stat_fondo)/(BR*Lumi*Acceptance*eff_tot))))
  
  stat_xsection_up = np.sqrt(np.dot(np.array(delta_xsection_stat_up),np.array(delta_xsection_stat_up)))
  stat_xsection_down = np.sqrt(np.dot(np.array(delta_xsection_stat_down),np.array(delta_xsection_stat_down)))
  #-------Incertidumbres estadísticas--------
  print('La seccion eficaz experimental del proceso ttbar es: %3.3f (+ %3.3f - %3.3f)(Stat.)(+ %3.3f - %3.3f)(Syst.) (+ %3.3f - %3.3f)(Lumi.) pb' %(xsection,stat_xsection_up,stat_xsection_down,delta_xsection_up_sys,delta_xsection_down_sys,delta_xsection_lumi_up,delta_xsection_lumi_down))
  plot.SaveCounts("MuonPt")
  plot.SaveCounts("EventWeight")
  plot.SaveCounts("EventWeight_gen_tot")
  plot.SaveCounts("MuonPt_gen")
  archivo = open(comando[2] + "/yields_MuonPt.txt","a")
  archivo.write('La seccion eficaz experimental del proceso ttbar es: %3.3f (+ %3.3f - %3.3f)(Stat.)(+ %3.3f - %3.3f)(Syst.) (+ %3.3f - %3.3f)(Lumi.) pb \n' %(xsection,stat_xsection_up,stat_xsection_down,delta_xsection_up_sys,delta_xsection_down_sys,delta_xsection_lumi_up,delta_xsection_lumi_down))
  archivo.write('La eficiencia de trigger para pt >= %3d GeV: %3.3f +- %3.3f \n' %(cortes_val[0],eff_trigg,(1-eff_trigg)/2))
  archivo.write('La eficiencia de btag es: %3.3f +- %3.3f \n' %(eff_btag,unc_eff_btag))
  archivo.write('La aceptancia es: %3.3f +- %3.3f \n' %(Acceptance, unc_Acceptance))
  archivo.write(' \n')
  archivo.write('%10s %10s \n' %('Sistematico','Impact'))
  cont = 0
  tot_sys = delta_xsection_up+delta_xsection_down
  tot_sys = np.sum(np.array(tot_sys))/2
  for nombre in nombres_sistematicos:
    impact = ((delta_xsection_up[cont]+delta_xsection_down[cont])/(2*tot_sys))*100
    archivo.write('%10s %10.3f \n' %(nombre,impact))
    cont += 1
    
    
  archivo.close()
  
  return
  
  
  #---Calculo xsection----------
  
  
  
drawer()



'''
print(r.kOrange+10)
print(r.kCyan)
print(r.kGray)
print(r.kGray+2)
print(r.kViolet-4)
print(r.kGreen-5)
print(r.kAzure-9)
print(r.kGreen+4)
'''

