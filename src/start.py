import generateTest
import subprocess, signal
#from dummy_ai import DummyAI
import os

from drivebuildclient.AIExchangeService import AIExchangeService
from drivebuildclient.aiExchangeMessages_pb2 import SimStateResponse

from drivebuildclient.aiExchangeMessages_pb2 import VehicleID
from drivebuildclient.AIExchangeService import AIExchangeService

from os.path import dirname, join
from pathlib import Path

from time import sleep

def _start_commonRoad_test():
    #from dummy_ai import DummyAI
    service = AIExchangeService("localhost", 8383)
    upload_result = service.run_tests("test", "test", Path(join(dirname(__file__), folder_path)))
    if upload_result and upload_result.submissions:
        for test_name, sid in upload_result.submissions.items():
            vid = VehicleID()
            vid.vid = "ego"
            #DummyAI(service).start(sid, vid)

def main():
    service = AIExchangeService("localhost", 8383)

    vid = VehicleID()
    vid.vid = "ego"

    myTest = generateTest.TestGenerator()
    # TODO Fixme
    for PATH_dbc, PATH_dbe in myTest.getTest():

        criteria = PATH_dbc
        environment = PATH_dbe

        submission_result = service.run_tests("test", "test", criteria,
                                              environment)
        # Interact with a simulation
        if submission_result and submission_result.submissions:
            for test_name, sid in submission_result.submissions.items():
                # Manoj, Yuki, Dinesh
                ai_process = subprocess.Popen(["C:\\sbse4tac-ws-2019-self-driving-car-smartcars\\.venv\\Scripts\\python.exe",
                                               "C:\\sbse4tac-ws-2019-self-driving-car-smartcars\\integration_with_DriveBuild\\trained_ai.py",
                                               sid.sid],
                                            cwd="C:\\sbse4tac-ws-2019-self-driving-car-smartcars\\integration_with_DriveBuild")



                # TODO Check if AI is actually running otherwise force the simulation to STOP
                while True:

                    print(sid.sid + ": Test status: " + service.get_status(sid))
                    sim_state = service.wait_for_simulator_request(sid, vid)
                    if sim_state is not SimStateResponse.SimState.RUNNING:
                        # TODO Use a trap or try except to ensure we kill the process
                        kill_process(ai_process)
                        print("Done")
                    else:
                        sleep(10)


if __name__ == '__main__':
    main()