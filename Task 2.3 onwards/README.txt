Requirements:
1. Copy the code folder to a C drive location.  Note that this folder includes data files that are required for the scripts to function.
2. Set up a new Python virtual environment (venv) as a subfolder "venv" of the base folder.
3. Activate the virtual environment in the terminal.
4. Change directory to where the base of the code folder.
5. Run "pip install -r requirements.txt".  This will install all the packages and specified versions.

Running - the scripts referenced below should run in the following sequence:
1. In the terminal, change directory to the base of the code folder containing the main Python scripts (e.g. task_2_3_main.py).
2. Ensure the virtual environment is activate.
3. Run "python task_2_3_main.py" to run the Python script for task 2.3 data creation.
4. Run "python task_2_4_main.py" to run the Python script for task 2.4 SPARQL.
5. Run "python task_2_5_1_main.py" to run the Python script for task 2.5 subtask 1 OA.1.
6. Run "python task_2_5_2_main.py" to run the Python script for task 2.5 subtask 2 OA.2.
7. For task 2.6, the steps are different:
    a. in the terminal, change directory into the sub-folder "Standalone_0.1".  There are the three config files (conf_1.cfg, conf_2.cfg and conf_3.cfg) to run separately for the sub-task Vector.1.
    b. run the command "python OWL2Vec_Standalone.py -config_file [default.cfg]".
        Replace the the .cfg file name with another to run under other configuration settings.
        This will run OWL2Vec according to the config file default.cfg.
    Note: the output files are output to the sub-folder "output_embedding".
    c. embedding files are saved to the sub-folder "output_embedding".  Rename them to  .
    d. Move them out of the folder to prevent being overwritten the next time to the top level folder.
    e. change directory to top of the folder where the main Python scripts are, then run "python task_2_6_main.py"
