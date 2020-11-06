import io
from PIL import Image
import predictSteeringAngle as pred
from xml.etree.ElementTree import Element, SubElement

class TrainAI:
    from drivebuildclient.AIExchangeService import AIExchangeService
    from drivebuildclient.aiExchangeMessages_pb2 import SimulationID, VehicleID

    def __init__(self, service: AIExchangeService) -> None:
        self.service = service


    @staticmethod
    def add_data_requests(ai_tag: Element, participant_id: str) -> None:
        try:
            SubElement(ai_tag, 'speed', id="egoSpeed")
            SubElement(ai_tag, 'camera', id="egoCamera", width="320", height="160", fov="120", direction="FRONT")

        except:
            raise NotImplementedError("Not implemented, yet.")


    def start(self, sid: SimulationID, vid: VehicleID) -> None:
        from drivebuildclient.aiExchangeMessages_pb2 import SimStateResponse, DataRequest, Control
        while True:
            print(sid.sid + ": Test status: " + self.service.get_status(sid))
            # Wait for the simulation to request this AI
            sim_state = self.service.wait_for_simulator_request(sid, vid)
            if sim_state is SimStateResponse.SimState.RUNNING:  # Check whether simulation is still running
                # Request data this AI needs
                request = DataRequest()
                request.request_ids.extend(["egoSpeed","egoCamera"])  # Add all IDs of data to be requested
                data = self.service.request_data(sid, vid, request)  # Request the actual data

                camera_image = Image.open(io.BytesIO(data.data["egoCamera"].camera.color)) # Converting camera images from the binary format
                steering_command = pred.predict_model(camera_image) # Prediction of steering angle from the camera image

                # Calculate commands controlling the car
                control = Control()
                # Define a control command like
                control.avCommand.accelerate = 1.0    # <Some value between 0.0 and 1.0>
                control.avCommand.steer = steering_command    # <Some value between -1.0 (left) and 1.0 (right)
                control.avCommand.brake = 0.0    # <Some value between 0.0 and 1.0>
                self.service.control(sid, vid, control)
            else:
                print(sid.sid + ": The simulation is not running anymore (Final state: "
                      + SimStateResponse.SimState.Name(sim_state) + ").")
                print(sid.sid + ": Final test result: " + self.service.get_result(sid))
                # Clean up everything you have to
                break

