import os
import imageio
import cv2
import numpy as np
from scipy.signal import convolve2d

directory = '.'						# working directory
filename = 'B:\\Footbawwll\\LSU_BAMA_2019.mp4'								# input video file

vid = imageio.get_reader(filename)
fps = vid.get_meta_data()['fps']
# print(str(fps) + ' FPS')

# # make output directory if necessary
# if not os.path.exists(out_dir):
#     os.makedirs(out_dir)

# out_vid = imageio.get_writer(os.path.join(out_dir, out_file), fps=fps)

# main loop through each frame in video
image_num = 0
for image in vid:
	if image_num == 0:
		bgr_image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
		cv2.imshow('235', bgr_image)
		cv2.waitKey(0)

		frame_hsv = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

		for c in range(3):
			cv2.imshow(str(c), frame_hsv[:, :, c])
			cv2.waitKey(0)

		hue = frame_hsv[:, :, 0]
		sat = frame_hsv[:, :, 1]
		val = frame_hsv[:, :, 2]
		median_hue = np.median(frame_hsv[:, :, 0])
		
		green = np.logical_and(hue > median_hue - 10, hue < median_hue + 10)

		white = np.logical_and(val > 215, sat < 40)
		green = np.logical_and(green, np.logical_not(white))

		green = (green * 255).astype(np.uint8)
		white = (white * 255).astype(np.uint8)

		cv2.imshow('green', green)
		cv2.waitKey(0)

		cv2.imshow('white', white)
		cv2.waitKey(0)

		green_edges = cv2.Canny(green, 100, 200, apertureSize=3)
		white_edges = cv2.Canny(white, 100, 200, apertureSize=3)

		cv2.imshow('green edges', green_edges)
		cv2.waitKey(0)
		cv2.imshow('white edges', white_edges)
		cv2.waitKey(0)

		gw_edges = (255 * np.logical_and(green_edges, white_edges)).astype(np.uint8)
		cv2.imshow('green/white edges', gw_edges)
		cv2.waitKey(0)

		frame_gray = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
		edges = cv2.Canny(frame_gray, 100, 200, apertureSize=3)
		edges -= gw_edges
		edge_avg = convolve2d(edges, np.ones((25, 25)) / 225.0, mode='same')
		cv2.imshow('edges', edges)
		cv2.waitKey(0)

		cv2.imshow('edges average', edge_avg.astype(np.uint8))
		cv2.waitKey(0)

		edge_avg_thresh = (255 * (edge_avg > 75)).astype(np.uint8)
		cv2.imshow('edges average thresh', edge_avg_thresh.astype(np.uint8))
		cv2.waitKey(0)

		many_edges = np.array((edge_avg < 75).astype(np.uint8))
		kill_spots = cv2.erode(many_edges, np.ones((15, 15))).astype(np.uint8)
		cv2.imshow('kill spots', (255 * kill_spots).astype(np.uint8))
		cv2.waitKey(0)
		cv2.destroyAllWindows()

		edges = (edges * kill_spots).astype(np.uint8)
		cv2.imshow('edges', edges)
		cv2.waitKey(0)

		minLineLength = 50
		maxLineGap = 25
		lines = cv2.HoughLinesP(edges, 1, np.pi/180, 80, minLineLength=minLineLength, maxLineGap=maxLineGap)
		# lines = cv2.HoughLinesP(gw_edges, 1, np.pi/180, 80, minLineLength=minLineLength, maxLineGap=maxLineGap)
		slopes = []
		endpts = []
		lines_bw_img = np.zeros(frame_gray.shape)
		for x in range(0, min(len(lines), 40)):
			for x1, y1, x2, y2 in lines[x]:
				cv2.line(bgr_image, (x1, y1), (x2, y2), (0, 0, 255), 1)
				cv2.line(lines_bw_img, (x1, y1), (x2, y2), 255, 1)
				slope = (y2 - y1) / (x2 - x1)
				center = (0.5 * (x1 + x2), 0.5 * (y1 + y2))
				print(slope, center)
				slopes.append(slope)
				endpts.append((x1, y1, x2, y2))

		median_slope = np.median(slopes)
		hull_pts = []
		for n in range(len(slopes)):
			if np.sign(slopes[n]) == np.sign(median_slope):
				x1, y1, x2, y2 = endpts[n]
				cv2.line(bgr_image, (x1, y1), (x2, y2), (0, 255, 255), 2)
				hull_pts.append((x1, y1))
				hull_pts.append((x2, y2))

		hull_pts = np.array(hull_pts)
		hull = cv2.convexHull(hull_pts)
		cv2.drawContours(bgr_image, [hull], 0, (0, 255, 192), 2)

		cv2.imshow('lines and hull', bgr_image)
		cv2.waitKey(0)

		### line of scrimmage finder
		edge_avg_og = edge_avg.copy()
		mask = np.zeros(edge_avg.shape)
		cv2.drawContours(mask, [hull], 0, 1, -1)
		for n in range(10):
			edge_avg = edge_avg_og.copy()
			edge_avg[edge_avg < 100] = 0.0
			edge_avg *= mask
			edge_avg /= np.max(edge_avg)
			edge_avg *= 255
			indices = np.indices(edge_avg.shape)
			y_avg = np.sum(indices[0] * edge_avg) / np.sum(edge_avg)
			x_avg = np.sum(indices[1] * edge_avg) / np.sum(edge_avg)
			print('centroid', x_avg, y_avg)
			mask = np.zeros(edge_avg.shape)
			cv2.circle(mask, (x_avg.astype(int), y_avg.astype(int)), 150, 1, -1)
		
		x_avg_int = x_avg.astype(int)
		y_avg_int = y_avg.astype(int)

		cv2.circle(edge_avg_og, (x_avg_int, y_avg_int), 3, 255, -1)
		cv2.imshow('edges average', edge_avg_og.astype(np.uint8))
		cv2.waitKey(0)

		cv2.circle(bgr_image, (x_avg_int, y_avg_int), 10, (0, 0, 255), 3)
		cv2.imshow('ball location', bgr_image)
		cv2.waitKey(0)

		cv2.imshow('BW lines', lines_bw_img)
		cv2.waitKey(0)
		
		x_scrim_line = lines_bw_img[x_avg_int, :]


		break
	image_num += 1

cv2.destroyAllWindows()