import numpy as np
import matplotlib.pyplot as plt

from skimage import data, color
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
from skimage.draw import circle_perimeter
from skimage.util import img_as_ubyte
import cv2

# https://scikit-image.org/docs/stable/auto_examples/edges/plot_circular_elliptical_hough_transform.html


# Load picture and detect edges
image = cv2.imread('screenshot4.png')
image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image = img_as_ubyte(image)
edges = canny(image, sigma=3, low_threshold=10, high_threshold=50)
cimage = cv2.Canny(image, 100,150)
# Detect two radii
hough_radii = np.arange(20, 35, 2)
hough_res = hough_circle(edges, hough_radii)

# Select the most prominent 3 circles
accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii,
                                           total_num_peaks=5)

# Draw them
fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 3))
image = color.gray2rgb(image)
PRECISIONY = 30
PRECISIONX = 50
PRECISIONR = 5
RREAL = 32
precisey = [y//PRECISIONY for y in cy]
precisex = [x//PRECISIONX for x in cx]

#Xs should line up, Ys should not.
xs = []
ys = []
rs = []
for center_y, center_x, radius in zip(cy, cx, radii):
    myy = center_y//PRECISIONY
    myx = center_x//PRECISIONX
    if(precisey.count(myy) == 1):
        if(precisex.count(myx) != 1) and abs(radius-RREAL)<=PRECISIONR:
            circy, circx = circle_perimeter(center_y, center_x, radius,
                                    shape=image.shape)
            image[circy, circx] = (220, 20, 20)
            xs.append(center_x)
            ys.append(center_y)
            rs.append(radius)
    else:
        precisey.remove(myy)
print(rs)
ax.imshow(image, cmap=plt.cm.gray)
plt.show()
assert len(xs)==len(ys)==len(rs)==2
cv2.imshow('',cimage)
cv2.waitKey(0) & 0xFF
dbx, dby, dbr = xs[0], ys[0], rs[0]
hx, hy, hr = xs[1], ys[1], rs[0]
if(hy < dby):
    dbx, dby, dbr, hx, hy, hr = hx, hy, hr, dbx, dby, dbr
handle = 1


deadbolt = cimage[dby-dbr:dby+dbr, dbx-dbr:dbx+dbr]
handle = cimage[hy-hr:hy+hr, hx-hr:hx+hr]
cv2.destroyAllWindows()