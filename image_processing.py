from PIL import Image
from os import path
from scheme import Scheme, np
#from math import dist, sqrt


def split_parts_list(n, k, prime, img, path_pic):
    h, w, rgb = img.shape  # height, image width, channel
    name, ext = path.splitext(path_pic)  # split to image path and extension
    np_lists = np.zeros(shape=(n, h, w, 3))
    # np_lists = [[] for i in range(n)] # blank list, for shares of picture
    shrs = [[[[] for j in range(w)] for i in range(h)],
            [[[] for j in range(w)] for i in range(h)],
            [[[] for j in range(w)] for i in range(h)]]
    # share values for each pixel RGB : shrs[0] is red ...
    # the image is a matrix = a series of rows of pixels
    row_count = 0
    for row in img:  # for each row in img
        new_rows = np.zeros(shape=(n, w, 3))
        # we make new rows, ie as many rows as we have division = n
        pix_count = 0
        for pix in row:
            if len(pix) == 3:
                r, g, b = pix[0], pix[1], pix[2]  # check that the pixel is plain => three values => RGB

            else:  # or has 4 values, where the alpha indicator is the first value
                r, g, b = pix[1], pix[2], pix[3]
            p1, p2, p3 = Scheme(r, n, k, prime), Scheme(g, n, k, prime), Scheme(b, n, k, prime)
            # each color value in a pixel is divided by SSSA into n values
            sh1, sh2, sh3 = p1.construct_shares_image(), p2.construct_shares_image(), p3.construct_shares_image()
            for i in range(n):
                new_rows[i][pix_count] = [sh1[i + 1], sh2[i + 1],
                                          sh3[i + 1]]  # we add newly created pixels to existing strings of new images
            shrs[0][row_count][pix_count] = sh1
            shrs[1][row_count][pix_count] = sh2
            shrs[2][row_count][pix_count] = sh3
            pix_count += 1
        row_count += 1
        # print(row_count)
        v = 0

        for el in range(n):
            np_lists[el][row_count - 1] = new_rows[el]  # adding the entire row to the shares matrix - image
            v += 1
    i = 0
    for image in np_lists:
        new_img = Image.fromarray(image.astype('uint8'))
        # creating shares - images from newly created matrices
        storage = name + "_share" + str(i)
        storage += ".png"
        new_img.save(storage)
        i += 1
    return shrs


def reconstruct_image(images, k, prime, shares):
    imgs = [np.array(Image.open(i)) for i in images]
    row_count = 0
    mat_len, row_len, rgb = imgs[0].shape
    len_imgs = len(imgs)
    matrix = [[] for i in range(mat_len)]
    need_calc = []
    img_dict = {}
    rec_info = {}
    counter = 0
    for row in imgs[0]:
        rec_pix = [[] for i in range(row_len)]
        pix_count = 0
        for pix in row:
            shares_r = []
            shares_g = []
            shares_b = []
            save = False
            num = 0
            for j in range(len_imgs):
                red, green, blue = imgs[j][row_count][pix_count][0], imgs[j][row_count][pix_count][1], \
                                   imgs[j][row_count][pix_count][2]
                if (red == 0 or blue == 0 or green == 0) and ([row_count, pix_count] not in need_calc):
                    need_calc.append([row_count, pix_count])
                    img_dict[counter] = [red, green, blue]
                    save = True
                    num = j
                shares_r.append(red)
                shares_g.append(green)
                shares_b.append(blue)
            if save:
                rec_info[counter] = [num, shares_r, shares_g, shares_b]
                counter += 1
            r, g, b = int(Scheme.reconstruct_secret_img(shares[0][row_count][pix_count], shares_r, k, prime)), \
                      int(Scheme.reconstruct_secret_img(shares_r[1][row_count][pix_count], shares_g, k, prime)), \
                      int(Scheme.reconstruct_secret_img(shares[2][row_count][pix_count], shares_b, k, prime))

            if r == 256:
                r = 0
            if g == 256:
                g = 0
            if b == 256:
                b = 0
            rec_pix[pix_count] = [r, g, b]
            pix_count += 1
        matrix[row_count] = rec_pix
        row_count += 1
    matrix = np.asarray(matrix)
    for i in range(len(need_calc)):
        [red, green, blue] = img_dict[i]
        [row_count, pix_count] = need_calc[i]
        [r, g, b] = matrix[row_count][pix_count]
        R, G, B = np.linalg.norm(i, need_calc[i][0], need_calc[i][1], [r, g, b], [red, green, blue], rec_info, matrix, shares, k, prime)
        matrix[need_calc[i][0]][need_calc[i][1]] = [R, G, B]
    return matrix
