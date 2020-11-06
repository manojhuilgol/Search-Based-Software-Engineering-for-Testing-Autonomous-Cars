import generateScenario
from pathlib import Path
from typing import Optional, Tuple
from xml.etree import ElementTree as ET
import generateScenario
from xml.etree.ElementTree import SubElement
import os
#import dummy_ai

class TestGenerator:

    def getTest(self) -> Optional[Tuple[Path, Path]]:

        try:
            # To run five random test criteria for the loaded scenario
            for file in os.listdir(generateScenario.COMMONROAD_SCENARIO_PATH):
                for i in range(1, 6):
                    file_name = os.path.splitext(file)[0]
                    scenario = os.path.join(generateScenario.COMMONROAD_SCENARIO_PATH, file)

                    if scenario.endswith(".xml"):
                        self.chain_of_keys, self.total_points, PATH_dbe = generateScenario.parseScenario(scenario, file_name, i)

                        PATH_dbc = generateScenario.generate_criterion(self.chain_of_keys, self.total_points, file_name, i)
                        print('Test instance ', i)

                         # Adding AI tags
                        myTree = ET.parse(PATH_dbc)
                        myRoot = myTree.getroot()
                        ET.register_namespace("", "http://drivebuild.com")
                        for elements in myRoot[6]:
                            element = elements

                        ai_tag = SubElement(element, 'ai')
                        #participant_ID = 'Manoj'
                        #dummy_ai.add_data_requests(ai_tag, participant_ID)
                        # SubElement(ai_tag, 'speed', id="egoSpeed")
                        SubElement(ai_tag, 'camera', id="egoFrontCamera", width="320", height="160", fov="120", direction="FRONT")

                        final_root = ET.ElementTree(myRoot)
                        with open(PATH_dbc, 'wb') as files:
                            final_root.write(files)

                        yield Path(PATH_dbc), Path(PATH_dbe)

                    else:
                        print('The scenario should be in the XML format')

        except Exception as e:
            raise NotImplementedError("Not implemented, yet.")