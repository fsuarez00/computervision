# get width & height of image
# google returns normalized vertices of bounding boxes relative to original image
# (normalized(x) * width, normalized(y) * height) -> (x, y) vertice based on scale of image
import json
import math
from PIL import Image


def is_parking_probable(data, image_file_path):
	img = Image.open(image_file_path)
	width, height = img.size
	print(width, height)

	is_label_parking_label = False

	object_annotations = data['localizedObjectAnnotations']
	i = 0
	# remove non-cars
	while i < len(object_annotations):
		obj = object_annotations[i]
		if obj['name'] != 'Car':
			object_annotations.remove(obj)
			continue
		i += 1

	cars = []  # sorted by x, left to right
	min_i = 0
	min_x = 0
	i = 0
	while i < len(object_annotations):
		obj = object_annotations[i]

		poly = obj['boundingPoly']
		normalized_vertices = poly['normalizedVertices']
		for normalized_vertex in normalized_vertices:
			normal_x = normalized_vertex['x']
			if min_x == 0 or normal_x < min_x:
				min_x = normal_x
				min_i = i

		i += 1
		if i == len(object_annotations):
			min_obj = object_annotations[min_i]
			cars.append(min_obj)
			object_annotations.remove(min_obj)
			min_i = 0
			min_x = 0
			i = 0

	label_annotations = data['labelAnnotations']
	for label in label_annotations:
		if label['description'] == 'Parking':
			if label['score'] >= 0.5:
				is_label_parking_label = True
			break

	if len(cars) is 1:
		return True

	norm_avgs = []
	for i in range(len(cars)):
		if i % 2 is not 0:
			continue

		# get right vertices
		bottom_right_x = cars[i]['boundingPoly']['normalizedVertices'][1]['x']
		bottom_right_y = cars[i]['boundingPoly']['normalizedVertices'][1]['y']
		top_right_x = cars[i]['boundingPoly']['normalizedVertices'][2]['x']
		top_right_y = cars[i]['boundingPoly']['normalizedVertices'][2]['y']

		# get left vertices
		bottom_left_x = cars[i+1]['boundingPoly']['normalizedVertices'][0]['x']
		bottom_left_y = cars[i+1]['boundingPoly']['normalizedVertices'][0]['y']
		top_left_x = cars[i+1]['boundingPoly']['normalizedVertices'][3]['x']
		top_left_y = cars[i+1]['boundingPoly']['normalizedVertices'][3]['y']

		# top euclidean distance
		top_delta_x = top_right_x - top_left_x
		top_delta_y = top_right_y - top_left_y
		top_d = math.sqrt((top_delta_x ** 2) + (top_delta_y ** 2))
		print("Top distance: " + str(top_d))

		# bottom euclidean distance
		bottom_delta_x = bottom_right_x - bottom_left_x
		bottom_delta_y = bottom_right_y - bottom_left_y
		bottom_d = math.sqrt((bottom_delta_x ** 2) + (bottom_delta_y ** 2))
		print("Bottom distance: " + str(bottom_d))

		avg_d = (top_d + bottom_d) / 2
		print("Average distance: " + str(avg_d))

		norm_avgs.append(avg_d)

	# analyze pairs

	return norm_avgs


# with open('StreetViewScrape/test_single_car.json') as f:
# 	google_res = json.load(f)
#
# image_file = 'StreetViewScrape/images/street_parking_7.png'

with open('StreetViewScrape/test_single_car.json') as f:
	google_res = json.load(f)

image_file = 'StreetViewScrape/images/street_parking_3.png'

print(is_parking_probable(google_res, image_file))
