# Command line to run with parameter scan on PC version of CC3D:
```
cmd.exe /c "< absolute path to paramScan.bat>" --input="< absolute path to cc3d file>" --output-dir="< absolute path to output directory of parameter scan>" --install-dir="< installation path to CompuCell3D folder>" --gui --output-frequency=50 --screenshot-output-frequency=50
```
# Command line to run cc3d.bat on PC version of CC3D:
```
cmd.exe /c "< absolute path to cc3d.bat>" --input="< absolute path to cc3d file of simulation project>"
```

# Delete unnecessary .vtk files with following command
```
find . -name "*.vtk" -type f
```
