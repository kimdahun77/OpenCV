import numpy as np
import cv2
from matplotlib import pyplot as plt

MIN_MATCH_COUNT = 4

img1 = cv2.imread(r'C:\Users\ASUS\Desktop\visionsys\room_left.jpg', 0)
img2 = cv2.imread(r'C:\Users\ASUS\Desktop\visionsys\room_right.jpg', 0)#same place, diffrent perspective
orimg1 = img1

cv2.imshow("right image", img1)
cv2.imshow("left image", img2)

sift = cv2.SIFT_create()

kp1, des1 = sift.detectAndCompute(img1,None) #특징점과 설명자
kp2, des2 = sift.detectAndCompute(img2,None)

FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)

flann = cv2.FlannBasedMatcher(index_params,search_params)
matches = flann.knnMatch(des1,des2,k=2)

good = []
for m, n in matches:
    if m.distance < 0.9*n.distance:
        good.append(m)

if len(good)>MIN_MATCH_COUNT:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1,1,2)

    M, mask = cv2.findHomography(src_pts, dst_pts)


    matchesMask = mask.ravel().tolist()

    h, w = img1.shape
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts,M)

    img2 = cv2.polylines(img2,[np.int32(dst)], True, 255, 3, cv2.LINE_AA)
    #cv2.imshow("left image2", img2)

else:
    print("Not enough matches are found - %d/%d" % (len(good), MIN_MATCH_COUNT))
    matchesMask = None

draw_params = dict(matchColor = (0, 255, 0),
                   singlePointColor = None,
                   matchesMask = matchesMask,
                   flags = 2)

img3 = cv2.drawMatches(img1, kp1, img2, kp2, good, None, **draw_params)

plt.imshow(img3, 'gray'), plt.show()


width = img2.shape[1] + img1.shape[1]
height = img2.shape[0] + img1.shape[0]

dst = cv2.warpPerspective(orimg1, M, (width, height))

cv2.imshow("Warping right to left", dst), plt.show()

dst[0:img2.shape[0], 0:img2.shape[1]] = img2

cv2.imshow("Stiching", dst), plt.show()

cv2.waitKey(0)