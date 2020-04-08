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
    if i == 'NJet':
        plot.SetYaxislog()
    plot.Stack(i)
    contador += 1
  #---Seleccion de graficas a pintar---
  eff_trigg = plot.Trigger_Eff("MuonPt", "MuonPt_notrigg","MuonPt_forEff","MuonPt_notrigg_forEff")
  
  #---Calculo xsection----------
  yields_ttbar, tot_MC, datos = plot.PrintCounts("MuonPt")
  yields_ttbar_gen, tot_MC_gen, datos_gen = plot.PrintCounts("MuonPt_gen")
  Lumi = 50
  BR = 0.09732
  '''
  BR = 0.22477
  '''
  Acceptance = yields_ttbar_gen/(BR*7929.47582548) #7929.47582548 es el numero total de eventos simulados de ttbar pesados
  eff_muons = 0.99
  eff_btag = 0.8
  eff_tot = eff_trigg*eff_muons*eff_btag
  xsection = (datos-(tot_MC-yields_ttbar))/(BR*Lumi*Acceptance*eff_tot)
  print('La seccion eficaz experimental del proceso ttbar es: %3.3f pb' %xsection)
  
  plot.SaveCounts("MuonPt")
  archivo = open(comando[2] + "/yields_MuonPt.txt","a")
  archivo.write("xsection_obs = %4.4f pb\nA = %4.4f \neff = %4.4f \n" %(xsection,Acceptance,eff_tot))
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

#Puede estar guay mirar el trigger con eta
