#!/bin/bash
login="lguerrot-23"
localFolder="/Users/lucasguerrot/Dropbox (Maestral)/Mes Documents/Documents/Cours + Etudes/EMSST BGD/BGD701 - Systèmes répartis pour le Big Data/TP/"
folderName="TP/"
#remoteFolder="/tmp/$login/instructions/"
remoteFolder2="/tmp/$login/"
#you can get the list of machines using the getMachines.sh script that creates a file named machines.txt
computers=($(cat machines.txt))
#computers=("tp-1a226-01" "tp-1a226-02" "tp-1a226-03" "tp-1a226-04" "tp-1a226-05")

for c in ${computers[@]}; do
  #this command is used to kill all the user processes (in case the program is already running)
  #then it removes the remote folder and creates a new one
  command0=("ssh" "$login@$c" "lsof -ti | xargs kill -9 2>/dev/null; rm -rf $remoteFolde2r;mkdir $remoteFolder2")
  #this command copies the folder to the remote folder
  command1=("scp" "-r" "$localFolder" "$login@$c:$remoteFolder2")
  #command1=("scp" "-r" "$localFolder$folderName" "$login@$c:$remoteFolder")
  #this command compiles the file and runs it (if the file is a java file named Server.java)
  #command2=("ssh" "$login@$c" "cd $remoteFolder$folderName;javac *.java;java Server")
  #here is an example for python (if the file is a python file named Server.py):
  #command2=("ssh" "-tt" "$login@$c" "cd $remoteFolder$folderName;sleep 3; python3 -m server.py")
  command2=("ssh" "-tt" "$login@$c" "cd $remoteFolder2$folderName;sleep 3; python3 server.py")
  echo ${command0[*]}
  "${command0[@]}"
  echo ${command1[*]}
  "${command1[@]}"
  echo ${command2[*]}
  "${command2[@]}" &
done