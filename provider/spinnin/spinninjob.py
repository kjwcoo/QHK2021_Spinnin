#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json
from collections import Counter
from datetime import datetime, timezone
from time import sleep
from qiskit.providers import BaseJob
from qiskit.qobj import validate_qobj_against_schema
from qiskit.result import Result

class SpinninJob(BaseJob):
    def __init__(self, backend, qobj):
        super().__init__(backend, 0)

        self._creation_date = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

        self._qobj = qobj
        
    def submit(self):
        payload = {
            'language': 'JSON',
            'program': self._qobj.to_dict()
        }
        
        # Write QOBJ to local server
        title = 'local_config.txt'
        with open( title, 'w' ) as file:
            file.write( json.dumps( self._qobj.to_dict()[ "config" ]["n_qubits"] ) )

        title = 'local_exp.txt'
        with open( title, 'w' ) as file:
            file.write( json.dumps( self._qobj.to_dict()[ "experiments" ][0]["instructions"] ) )
        
        # Pass a trigger to the local server
        with open( 'status.txt', 'a' ) as file:
            file.write( 'start: '+self._creation_date+'\n')
        exec(open("driver.py").read())
        
    def result(self):
        
        shots = self._qobj.config.shots
        
        with open( 'status.txt', 'r' ) as file:
            counts = 100
            # counts = int( file.readlines()[-1] )
            
        experimental_results = [{
            'success': True,
            'shots': shots,
            'data': {'counts': counts}
        }]
        
        results = {
            'success': True,
            'backend_name': 'SpinninBackend',
            'backend_version': '0.0.1',
            'job_id': '0',		
            'qobj_id': '0',
            'results': experimental_results
        }
        print( results )
        self._result = results[ 'results' ][ 0 ][ 'data' ][ 'counts' ]
        
        return self._result

    def cancel(self):
        pass
    
    def status(self):
        pass


# In[ ]:




