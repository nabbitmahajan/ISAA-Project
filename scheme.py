from random import randint
from lagrange_polynomial import LagrangePolynomial, np


# implementation of secret sharing scheme
class Scheme(object):
    def __init__(self, s, n, k, p):

        """
        s: secret
        n: total number of shares
        k: recovery threshold
        p: prime, where p > n
        """
        self.s = s
        self.n = n
        self.k = k
        self.p = p
        # Generate random coefficients
        self.coefs = list(dict.fromkeys([randint(1, 65000) for i in range(1, k)]))

    def construct_shares_image(self):

        self.coefs.append(self.s)
        values = np.polyval(self.coefs, [i for i in range(1, self.n + 1)]) % self.p
        shares = {}
        for i in range(1, self.n + 1):
            if int(values[i - 1]) != 256:
                if int(values[i - 1]) == 0:
                    shares[self.n + 1] = 256
                    shares[i] = int(values[i - 1])
                else:
                    shares[i] = 0
                    shares[self.n + 1] = 256
        return shares

    def reconstruct_secret_img(shares: dict, inputs: list, k, p):

        if len(shares) < k:
            raise Exception("More shares needed")
        for el in inputs:
            if el not in shares.values():
                raise Exception("Inadequate share")
        indexi = []
        vals = np.array(list(shares.values()))
        for i in range(len(inputs)):
            search = inputs[i]
            if inputs[i] == 256:
                search = 0
            ii = np.where(vals == search)[0]
            lii = [list(shares.keys())[i] for i in ii]
            indexi.append(lii)
        lp = LagrangePolynomial(indexi, [shares[ind[0]] for ind in indexi])
        secret = lp.interpolate_img(0) % p
        return secret
