#!/usr/bin/python

class BliffObject(object):
    """
    Represents a generic Bliffoscope object
    """
    def __init__(self, fname):
        """
        Initializes BliffImage object and set filename prperty
        """
        self.fname = fname
        
    def loadImg(self):
        """
        Loads text file into 2d array of characters (self.img) filename is self.fname
        returns: nothing
        """
        ins = open( self.fname, "r" )
        img = []
        for line in ins:
            img.append(list(line.replace("\n","").replace("\r","")) )
        self.img = img

class BliffImage(BliffObject):
    """
    Represents a Bliffoscope image object
    """

    def getSubImg(self, x, y, h, w):
        """
        Method to return a subImg (2d array) from self.img
        arguments: 
            x: x-axis offset of most upper left point
            y: y-axis of upper left most point 
            h: height of sub image
            w: width of sub image
        returns:
            2D character array (list) [["+"],[" "],[]...]
        """
        idx = y
        temp = self.img[y:y+h]#get subList of height h
        returnList = []
        for row in temp:#trim the sublist to width w
            returnList.append(row[x:x+w])
        return returnList
        


class BliffTarget(BliffObject):
    """
    Represents a Bliffoscope target object
    """
        
    def getNumMatches(self,subImg):
        """
        Compares self.img to a 2D array of the same size, returns the number of points that match
        """
        matches, idx = 0, 0
        for row in self.img:
            matches += len([i for i, j in zip(self.img[idx], subImg[idx]) if i == j])
            idx += 1     
        return matches
        
    def getTotalPoints(self):
        """
        returns the total number of points in self.img (height * width)
        """
        return len(self.img)*len(self.img[0])
        
    @staticmethod
    def printImg(img):
        """
        Static method to print out a 2d array (img) as text
        """
        for row in img:
            print "".join(row)
        print "="*len(img[0])
            
def comparator(a ,b):
    returnval = 0
    if(a[1] > b[1]): 
        returnval = -1
    elif(a[1] < b[1]): 
        returnval = 1
    return returnval

def getMatches(haystack, needle, threshold):
    hh, nh, hw, nw = len(haystack.img), len(needle.img), len(haystack.img[0]), len(needle.img[0])
    returnList = []
    for idxh in xrange(hh - nh):#iterate through rows
        for idxw in xrange(hw - nw):#iterate through cols
            subImg = haystack.getSubImg(idxw, idxh, nh, nw)
            numMatches = needle.getNumMatches(subImg)
            if(numMatches >= threshold):
                #BliffTarget.printImg(subImg)
                returnList.append(([(idxw, idxh)], round(numMatches/float(needle.getTotalPoints()),3)))
    returnList.sort(comparator)
    return returnList
            

def binP(N, p, x1, x2):
    """
    http://stackoverflow.com/questions/13059011/is-there-any-python-function-library-for-calculate-binomial-confidence-intervals
    """
    p = float(p)
    q = p/(1-p)
    k = 0.0
    v = 1.0
    s = 0.0
    tot = 0.0

    while(k<=N):
            tot += v
            if(k >= x1 and k <= x2):
                    s += v
            if(tot > 10**30):
                    s = s/10**30
                    tot = tot/10**30
                    v = v/10**30
            k += 1
            v = v*q*(N+1-k)/k
    return s/tot

def calcBin(vx, vN, vCL = 95):
    '''
    Calculate the exact confidence interval for a binomial proportion

    Usage:
    >>> calcBin(13,100)    
    (0.07107391357421874, 0.21204372406005856)
    >>> calcBin(4,7)   
    (0.18405151367187494, 0.9010086059570312)
    ''' 
    vx = float(vx)
    vN = float(vN)
    #Set the confidence bounds
    vTU = (100 - float(vCL))/2
    vTL = vTU

    vP = vx/vN
    if(vx==0):
            dl = 0.0
    else:
            v = vP/2
            vsL = 0
            vsH = vP
            p = vTL/100

            while((vsH-vsL) > 10**-5):
                    if(binP(vN, v, vx, vN) > p):
                            vsH = v
                            v = (vsL+v)/2
                    else:
                            vsL = v
                            v = (v+vsH)/2
            dl = v

    if(vx==vN):
            ul = 1.0
    else:
            v = (1+vP)/2
            vsL =vP
            vsH = 1
            p = vTU/100
            while((vsH-vsL) > 10**-5):
                    if(binP(vN, v, 0, vx) < p):
                            vsH = v
                            v = (vsL+v)/2
                    else:
                            vsL = v
                            v = (v+vsH)/2
            ul = v
    return (dl, ul)

        
def main():
    from pprint import pprint
    bs = BliffImage("TestData.txt")
    bs.loadImg();
    st = BliffTarget("SlimeTorpedo.txt")
    st.loadImg();
    ss = BliffTarget("Starship.txt")
    ss.loadImg()
    """
    Find the (upper) confidence interval for a binomial distribution where p = .5,
    n = number of points in the target image and alpha (confidence level) is 99.9
    we will use the upper limit as the threshold for image detection
    """
    ll,ul = calcBin(st.getTotalPoints()/2, st.getTotalPoints(), 99.9)
    stUpperLim = ul*st.getTotalPoints()
    print "========SLIME TORPEDOS========"
    sts = getMatches(bs, st, stUpperLim)
    print "%s Slime Torpedos found." % len(sts)
    pprint(sts)
    
    ll,ul = calcBin(st.getTotalPoints()/2, ss.getTotalPoints(), 99.9)
    ssUpperLim = ul*ss.getTotalPoints()
    print "==========STARSHIPS=========="
    sss = getMatches(bs, ss, stUpperLim)
    print "%s Starships found." % len(sss)
    pprint(getMatches(bs, ss, ssUpperLim))
    print "SAMPLE"
    BliffTarget.printImg(bs.getSubImg(20,20,20,20))

    #unit tests
    #pprint(getSubList(bs, 0, 6, 2, 2))
    #print getNumMatches([['+', ' ', ' '],[' ', '+', ' ']],[['+', ' ', '+'],[' ', '+', ' ']])


if __name__ == "__main__":
    main()