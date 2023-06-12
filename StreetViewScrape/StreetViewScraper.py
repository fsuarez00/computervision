import requests
import urllib.parse as urlparse
import hashlib
import hmac
import base64
import os
import json
from PIL import Image
from io import BytesIO

# import google_streetview.api

key = "AIzaSyCyn9qBPS3hbb1aFicTCYRANmGwQYU5598"
sign_secret = 'MjkEAslqgQaPjfnWNcwg71w_6JA='


# params = [{
# 	'size': '640x640',
# 	'location':  '34.122342,-118.73721',
# 	'key': 'AIzaSyCyn9qBPS3hbb1aFicTCYRANmGwQYU5598'
# }]

# Create a results object
# results = google_streetview.api.results(params)

def meta_parse(meta_url, save_loc, filename):
	response = requests.get(meta_url)
	json_data = response.json()
	if json_data['status'] == "OK":

		with open(os.path.join(save_loc, filename + '.json'), 'w') as outfile:
			json.dump(json_data, outfile)

		pano_id = json_data['pano_id']
		if 'date' in json_data:
			return json_data['date'], pano_id  # sometimes it does not have a date
		else:
			return None, pano_id


PrevImage = []  # Global list that has previous images sampled, memoization kind of


def get_street_ll(lat, lon, head, filename, save_loc):
	base = 'https://maps.googleapis.com/maps/api/streetview'
	size = '?size=1024x768&fov=110&location='
	end = str(lat) + ',' + str(lon) + '&heading=' + str(head) + '&key=' + key
	my_url = base + size + end
	file = filename + '.jpg'
	metadata_url = base + '/metadata' + size + end
	print(my_url, metadata_url)
	met_lis = list(meta_parse(metadata_url, save_loc, filename))  # does not grab image if no date
	if (met_lis[1], head) not in PrevImage and met_lis[0] is not None:
		signed_url = sign_url(my_url, sign_secret)
		res = requests.get(signed_url)
		img = Image.open(BytesIO(res.content))
		img = img.save(os.path.join(save_loc, file))
		met_lis.append(img)
		PrevImage.append((met_lis[1], head))  # append new Pano ID to list of images
	else:
		met_lis.append(None)

	return met_lis


def sign_url(input_url=None, secret=None):
	""" Sign a request URL with a URL signing secret.
	      Usage:
	      from urlsigner import sign_url
	      signed_url = sign_url(input_url=my_url, secret=SECRET)
	      Args:
	      input_url - The URL to sign
	      secret    - Your URL signing secret
	      Returns:
	      The signed request URL
	  """
	if not input_url or not secret:
		raise Exception("Both input_url and secret are required")

	url = urlparse.urlparse(input_url)

	# We only need to sign the path+query part of the string
	url_to_sign = url.path + "?" + url.query

	# Decode the private key into its binary format
	# We need to decode the URL-encoded private key
	decoded_key = base64.urlsafe_b64decode(secret)

	# Create a signature using the private key and the URL-encoded
	# string using HMAC SHA1. This signature will be binary.
	signature = hmac.new(decoded_key, str.encode(url_to_sign), hashlib.sha1)

	# Encode the binary signature into base64 for use within a URL
	encoded_signature = base64.urlsafe_b64encode(signature.digest())

	original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query

	# Return signed URL
	return original_url + "&signature=" + encoded_signature.decode()


DataList = [(40.6331235, -74.0315358, 200)]

image_list = [] # to stuff the resulting meta-data for images
ct = 0
for i in DataList:
	ct += 1

	head = i[2]
	headings = [head]
	# calculate opposite heading
	opposite_head = 0
	if head < 180:
		opposite_head = (head + 200) - 20
	elif head > 180:
		opposite_head = (head - 200) + 20
	headings.append(opposite_head)

	for heading in headings:
		fi = "street_parking_" + str(ct) + '_' + str(heading)
		temp = get_street_ll(i[0], i[1], heading, fi, 'D:\\Projects\\ComputerVision\\StreetViewScrape\\images')
		if temp[2] is not None:
			image_list.append(temp)
