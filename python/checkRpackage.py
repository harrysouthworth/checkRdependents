def runRCMDcheck(path="tarballs"):
    """Run R CMD check on all tar.gz files found in path"""

    from os import listdir
    from os import system
    from os.path import isfile, join

    files = [f for f in listdir(path) if isfile(join(path, f))]
    
    for f in files:
        print("Checking " + f)
        system("cd " + path + "; R CMD check " + f + "> output.log")

def lookForProblems(path="tarballs"):
    """Find any instance of 'ERROR', 'WARNING' or 'NOTE' in the output of
       R CMD check"""

    from os import listdir
    from os.path import isfile, join
    
    dirs = [f for f in listdir(path) if not isfile(join(path, f))]

    for directory in dirs:
        print("\n" + "*"*20 + " " + directory[:-7] + " " + "*"*20 + "\n")
        for file in ["/00install.out", "/00check.log"]:
            infile = open(path + "/" + directory + file)
            for line in infile:
                if "ERROR" in line or "WARNING" in line or "NOTE" in line:
                    print(line)

def getDependents(package):
    """ Retrieve a package CRAN page and parse it to get a list of dependent
        packages. """
    
    from urllib import urlretrieve
    from bs4 import BeautifulSoup

    # Retrieve page, read it, turn into soup
    url = "http://cran.r-project.org/web/packages/" + package + "/index.html"
    localfile = "." + package + ".html"
    
    page = urlretrieve(url, localfile)
    page = open(localfile, "r").read()
    soup = BeautifulSoup("".join(page))

    # Grab the table of dependents
    deps = soup.find("table", {"summary" : "Package " + package + " reverse dependencies"})
    deps = deps.findAll("tr")[0] # First row
    deps = deps.findAll("a")
    res = []
    for d in deps:
        res.append(str(d.text))
    
    print("Dependent packages:")
    for d in res:
        print(d)


    return(res)

def getDependentTarNames(d):
    """ Take the names of some R packages and construct the name of
       the package source for the latest version. """

    from urllib import urlretrieve
    from bs4 import BeautifulSoup

    parturl = "http://cran.r-project.org/web/packages/"
    res = []

    for package in d:
        url = parturl + package + "/index.html"
        localfile = "." + package + ".html"

        page = urlretrieve(url, localfile)
        page = open(localfile, "r").read()
        soup = BeautifulSoup("".join(page))

        # Get the table with the file name in it
        smry = "Package " + package + " downloads"
        soup = soup.find("table", {"summary" : smry})
        soup = soup.findAll("tr")[0]
        soup = soup.findAll("a")

        for i in soup:
            res.append(str(i.text).strip())
        
    return(res)

def getPackages(packages, path="tarballs"):
    """ Download specified R package sources. """
    from urllib import urlretrieve
    
    parturl = "http://cran.r-project.org/src/contrib/"
    
    for package in packages:
        url = parturl + package
        print("Downloading " + package)
        urlretrieve(url, path + "/" + package)

def checkDependents(package, path="tarballs"):
    d = getDependents(package)
    d = getDependentTarNames(d)
    getPackages(d)
    runRCMDcheck()
    lookForProblems()


    

