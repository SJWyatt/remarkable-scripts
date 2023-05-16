# remarkable-scripts
A collection of scripts I find useful for interfacing with my remarkable. 

### find_notebooks.py
A python script to help in searching for notebooks. 
Returns file UUID and other information. Can be run directly on the Remarkable if python3 is installed. \
Basic usage: `python3 find_notebook.py -n "Search String" -f <path-to-xochitl>/` \
Run with `python3 find_notebook.py --help` for more detailed instructions.

### permanently_delete.py
A python script to permanently delete all notebooks that 
have already been deleted from the trash. \
(Note: Even though the "empty trash" button on the UI says it is 'permanently' deleting the files, they still actually exist on the filesystem.)
Basic usage: Run `python3 permanently_delete.py` on the Remarkable. \
Run with `python3 permanently_delete.py --help` for more detailed instructions.
