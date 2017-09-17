from functools import partial;
from functools import reduce;
import cv2;
import sys;

ObjsOfInterests = [];
DIST_THRESHOLD = 0.01;

def calcDist(prevCoords, currBlobCoord):
	return map(((x[0]-currBlobCoord[0])**2+(x[1]-currBlobCoord[1])**2), prevCoords);

def addToPath(blobsInFrame):
	if len(ObjsOfInterests) == 0:
		for currBlob in blobsInFrame:
			ObjsOfInterests.append({
				'coords': [(currBlob['cX'], currBlob['cY'])],
				'elapsedFrames': 1,
				'weight': currBlob['weight']
			});
	else:
		prevCoords = reduce((lambda x, y: x['coords'][-1]), ObjsOfInterests);
		for currBlob in blobsInFrame:
			currBlobCoord = (currBlob['cX'], currBlob['cY'])
			distToBlobs = calcDist(prevCoords, currBlobCoord);
			minDist = min(distToBlobs);
			blobIndex = distToBlobs.index(minDist);
			nearestPrevBlob = prevCoords[blobIndex];
			cv2.arrowedLine(img, nearestPrevBlob, currBlobCoord, color, thickness, lineType, shift)

			if minDist < DIST_THRESHOLD:
				ObjsOfInterests[blobIndex]['coords'][-1].append(currBlobCoord);
				ObjsOfInterests[blobIndex]['elapsedFrames']+=1;
				#ObjsOfInterests[blobIndex]['weight'] += currBlob['weight']
			else:
				ObjsOfInterests.append({
					'coords': currBlobCoord,
					'elapsedFrames': 1
					#'weight': blob['weight']
				})

