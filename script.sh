#!/bin/bash
echo "Enter command:"
read command
rm command.txt
echo $command >> command.txt