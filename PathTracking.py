from functools import partial;
from functools import reduce;

ObjsOfInterests = [];
DIST_THRESHOLD = 0.01;

calcDist = lambda s, d: (s[0]-d[0])**2+(s[1]-d[1])**2

def addToPath(currentBlobs):
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
			nearestPrevBlob = min(prevCoords, key=partial(calcDist, currBlobCoord))
			if calcDist(currBlobCoord, nearestPrevBlob) < DIST_THRESHOLD:
				blobIndex = [y for y in prevCoords].index(nearestPrevBlob);
				ObjsOfInterests[blobIndex]['coords'][-1].append(currBlobCoord);
				ObjsOfInterests[blobIndex]['elapsedFrames']+=1;
				ObjsOfInterests[blobIndex]['weight'] += currBlob['weight']
			else:
				ObjsOfInterests.append({
					'coords': currBlobCoord,
					'elapsedFrames': 1,
					'weight': blob['weight']
				})
	
