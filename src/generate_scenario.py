from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element, SubElement
import webbrowser
import glob
import os
import time
from random import randint


def parseScenario(SCENARIO, file_name, testInstance):
    myTree = ET.parse(SCENARIO)
    myRoot = myTree.getroot()

    tags = list()
    ids = list()
    for items in myRoot:
        tags.append(items.tag)
        ids.append(items.attrib)

    total_points = dict()



    indices = [index for index, item in enumerate(tags) if item == 'lanelet']  # Fetch the indices of 'lanelets' from the MYROOT list

    # Fetching the ID of all the lanelets
    lane_ids = list()
    for i in range(len(indices)):
        lane_ids.append(ids[i].get('id'))


    for items, index in zip(myRoot, indices):
        x_points_left = list()
        y_points_left = list()
        x_points_right = list()
        y_points_right = list()

        for i in myRoot[index][0].iter('x'):
            x_points_left.append(i.text)
        for j in myRoot[index][0].iter('y'):
            y_points_left.append(j.text)
        for i in myRoot[index][1].iter('x'):
            x_points_right.append(i.text)
        for j in myRoot[index][1].iter('y'):
            y_points_right.append(j.text)
        total_points[items.attrib.get('id')] = [x_points_left, y_points_left, x_points_right, y_points_right]

       # next_lanelet_id = myRoot[index][2].attrib.get('ref')  # To find the id written in the successor


    chain_of_keys = list()
    successor_keys = list()
    multi_successor = list()


# To interlink the lanelet ids based on the Successor
    for iter_id in total_points.keys():
        if iter_id in chain_of_keys: continue
        else:
            current_id = iter_id
            for items, index in zip(myRoot, indices):
                terminate_link = False
                if current_id == items.attrib.get('id'):
                    found_successor = False
                    successor_keys.append(current_id)
                    for i, tag in enumerate(myRoot[index]):
                        elem = [str(j) for j in myRoot[index]]
                        num_of_successors = len([i for i in range(len(elem)) if 'successor' in elem[i]])
                        if 'successor' in str(tag):
                            current_id = myRoot[index][i].attrib.get('ref')
                            if num_of_successors > 1:
                                while(num_of_successors > 1):
                                    multi_successor.append(myRoot[index][i].attrib.get('ref'))
                                    i += 1
                                    num_of_successors -= 1
                            found_successor = True
                    if not found_successor:
                        terminate_link = True
                        chain_of_keys.append(successor_keys)
                        successor_keys = []
                        break
                    if terminate_link == True: break

    uniques = list()
    for items in chain_of_keys:
        for e in items:
            if e not in uniques: uniques.append(e)

    x = list()
    y = list()
    x_r = list()
    y_r = list()
    for items in uniques:
        for e in total_points[items][0]:
            x.append(float(e))
        for e in total_points[items][1]:
            y.append(float(e))
        for e in total_points[items][2]:
            x_r.append(float(e))
        for e in total_points[items][3]:
            y_r.append(float(e))

    for chains in chain_of_keys:
        x_coord_left = list()
        y_coord_left = list()
        x_coord_right = list()
        y_coord_right = list()
        for i in chains:
            for items in total_points[i][0]:
                x_coord_left.append(float(items))
            for items in total_points[i][1]:
                y_coord_left.append(float(items))
            for items in total_points[i][2]:
                x_coord_right.append(float(items))
            for items in total_points[i][3]:
                y_coord_right.append(float(items))

# Storing those lanelet ids where there are mulltiple successors specified
    for ids in multi_successor:
        x_coord_left = list()
        y_coord_left = list()
        _coord_right = list()
        y_coord_right = list()

        for items in total_points[ids][0]:
            x_coord_left.append(float(items))
        for items in total_points[ids][1]:
            y_coord_left.append(float(items))
        for items in total_points[ids][2]:
            x_coord_right.append(float(items))
        for items in total_points[ids][3]:
            y_coord_right.append(float(items))


    # Generate a new XML file

    root = Element('environment', xmlns="http://drivebuild.com"
                   #xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance",
                   # xsi:schemaLocation="http://drivebuild.com drivebuild.xsd"
                    )


    SubElement(root, 'author').text = 'XYZ'
    SubElement(root, 'timeOfDay').text = "0"

    newTree = SubElement(root,'lanes')

    for chains in chain_of_keys:
        x_coord_left = list()
        y_coord_left = list()
        x_coord_right = list()
        y_coord_right = list()
        child_left = SubElement(newTree, 'lane', leftLanes="0")
        child_right = SubElement(newTree, 'lane', rightLanes="1")

        for i in chains:
            for items in total_points[i][0]:
                x_coord_left.append(float(items))
            for items in total_points[i][1]:
                y_coord_left.append(float(items))
            for items in total_points[i][2]:
                x_coord_right.append(float(items))
            for items in total_points[i][3]:
                y_coord_right.append(float(items))

            for a, b in zip(x_coord_left, y_coord_left):
                SubElement(child_left, 'laneSegment', x=str(a), y=str(b), width="5")
            for c, d in zip(x_coord_right, y_coord_right):
                SubElement(child_right, 'laneSegment', x=str(c), y=str(d), width="5")

    final_root = ET.ElementTree(root)

    PATH_FOLDER = os.path.join(SAVE_SCENARIO, file_name) + '/' 'Test_instance_' + str(testInstance)
    if not os.path.isdir(PATH_FOLDER): os.makedirs(PATH_FOLDER)
    PATH_dbe = os.path.join(PATH_FOLDER, file_name) + '.dbe.xml'


    with open(PATH_dbe,'wb') as files:
        final_root.write(files)

    return chain_of_keys, total_points, PATH_dbe


# Generate test criteria

def generate_criterion(chain_of_keys, total_points, file_name, testInstance):
    root = Element('criteria', xmlns="http://drivebuild.com",
                    #xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance",
                    #xsi:schemaLocation="http://drivebuild.com drivebuild.xsd"
                    )

    SubElement(root, 'author').text = 'XYZ'
    SubElement(root, 'version').text = '1'
    SubElement(root, 'name').text = str(file_name)
    SubElement(root, 'environment').text = str(file_name)+'.dbe.xml'
    SubElement(root, 'stepsPerSecond').text = '60'
    SubElement(root, 'aiFrequency').text = "6"

    participants = SubElement(root, 'participants')
    participant = SubElement(participants, 'participant', id="ego", model="ETK800")


    positions = fetch_positions(chain_of_keys, total_points)  # Returns the start and success coordinates for the criteria as a dictionary

    startX = str(positions['startPositions'][0])
    startY = str(positions['startPositions'][1])

    endX = str(positions['successPositions'][0])
    endY = str(positions['successPositions'][1])

    SubElement(participant, 'initialState', x=startX, y=startY, orientation="0", movementMode="MANUAL", speed="50")

   # ai = SubElement(participant,'ai')
   # SubElement(ai, 'speed', id="egoSpeed")
   # SubElement(ai, 'camera', id="egoCamera", width="320", height="160", fov="120", direction="FRONT")

    # FOR SPECIFYING WAYPOINTS
    movement = SubElement(participant, 'movement')
    for waypoint_x, waypoint_y in zip(positions['wayPointsX'], positions['wayPointsY']):
        SubElement(movement, 'waypoint', x=str(waypoint_x), y=str(waypoint_y), tolerance="4", movementMode=CURRENT_MODE, speedLimit="1000")

    # Generating pre-conditions for the test criteria
    precondition = SubElement(root, 'precondition')
    vcPosition = SubElement(precondition, 'vcPosition', participant="ego", x="-4", y="4", tolerance="4")
    subChild = SubElement(vcPosition, 'not')
    scSpeed =  SubElement(subChild, 'scSpeed', participant="ego", limit="15")

    # Success criteria
    success = SubElement(root, 'success')
    SubElement(success, 'scPosition', participant="ego", x=endX, y=endY, tolerance="5")

    # Failure criteria
    failure = SubElement(root, 'failure')
    subChildOr = SubElement(failure, 'or')
    SubElement(subChildOr, 'scDamage', participant="ego")
    SubElement(subChildOr, 'scLane', participant="ego", onLane="offroad")


    final = ET.ElementTree(root)

    PATH_FOLDER = os.path.join(SAVE_SCENARIO, file_name) + '/' 'Test_instance_' + str(testInstance)

    PATH_dbc = os.path.join(PATH_FOLDER, file_name) + '.dbc.xml'

    with open(PATH_dbc,'wb') as files:
        final.write(files)

    return PATH_dbc


def fetch_positions(chain_of_keys, total_points):

    x_coord_left = list()
    y_coord_left = list()
    x_coord_right = list()
    y_coord_right = list()

    for chains in chain_of_keys:

        for i in chains:
            for items in total_points[i][0]:
                x_coord_left.append(float(items))
            for items in total_points[i][1]:
                y_coord_left.append(float(items))
            for items in total_points[i][2]:
                x_coord_right.append(float(items))
            for items in total_points[i][3]:
                y_coord_right.append(float(items))

    coordinates = [x_coord_left, y_coord_left, x_coord_right, y_coord_right]
    lenOfRoad = len(coordinates[0])
    randomIndex = randint(1, lenOfRoad-1)
    roadLane = {'0':[0, 1], '1':[2, 3]}    # '0' for leftLane and '1' for right Lane
    lane = roadLane[str(randint(0, 1))]

    startPointX = coordinates[lane[0]][randomIndex]
    startPointY = coordinates[lane[1]][randomIndex]

    if randomIndex < (lenOfRoad/2):
        successPositionX = coordinates[lane[0]][lenOfRoad-1]  # Initialize successPoint to be the end Point
        successPositionY = coordinates[lane[1]][lenOfRoad-1]

        wayPointsX = list()
        wayPointsY = list()

        for points in range(randomIndex, lenOfRoad-2, 2):
            wayPointsX.append(coordinates[lane[0]][points])
            wayPointsY.append(coordinates[lane[1]][points])

    else:
        successPositionX = coordinates[lane[0]][0]   # Initialize successPoint to be the starting Point
        successPositionY = coordinates[lane[1]][0]

        wayPointsX = list()
        wayPointsY = list()

        for points in range(1, lenOfRoad//2, 2):
            wayPointsX.append(coordinates[lane[0]][points])
            wayPointsY.append(coordinates[lane[1]][points])


        if (abs(float(wayPointsX[0]) - float(startPointX)) > (abs(float(wayPointsX[-1]) - float(startPointX)))):
            wayPointsX.reverse()
            wayPointsY.reverse()

    maxWayPoints = 20
    sparseness = len(wayPointsX) // maxWayPoints

    xWayP = list()
    yWayP = list()

    # Reducing the number of way points to maximum count of 20
    if len(wayPointsX) > 20:
        for i in range(0, len(wayPointsX), sparseness):
            xWayP.append(wayPointsX[i])
            yWayP.append(wayPointsY[i])
    else: xWayP, yWayP = wayPointsX, wayPointsY

    print('Start Position: ', (startPointX, startPointY))
    print('End Position: ', (successPositionX, successPositionY))
    print('Way Points: \n', xWayP, yWayP)

    return {
            'startPositions': [startPointX, startPointY],
            'successPositions': [successPositionX, successPositionY],
            'wayPointsX': xWayP,
            'wayPointsY': yWayP
            }



# coordinates = parseScenario('F:/ParseXML/DEU_Ffb-1_7_T-1.xml')
# generate_criterion(coordinates)



AIMODES = {'BeamngAI': '_BEAMNG', 'TrainedAI': 'AUTONOMOUS', 'ManualMode': 'MANUAL'}
CURRENT_MODE = AIMODES['BeamngAI']
SCENARIO = None
URL = "https://commonroad.in.tum.de/scenarios/"
COMMONROAD_SCENARIO_PATH = os.path.join(os.path.dirname(__file__), 'commonroad_scenarios')
SAVE_SCENARIO = os.path.join(os.path.dirname(__file__), 'drivebuild_scenarios')


# REFERENCES:

# https://stackoverflow.com/questions/45822480/python-how-do-i-open-the-most-recent-file-in-my-downloads-directory
# # https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-given-a-list-containing-it-in-python
# https://stackoverflow.com/questions/9764298/is-it-possible-to-sort-two-listswhich-reference-each-other-in-the-exact-same-w