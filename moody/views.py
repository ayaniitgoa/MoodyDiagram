import math
from django.shortcuts import render


def plot(rey, length=1.0, D=0.0254, dens=997.0, viscosity=5.47e-4, k=0.0001):
    # constants
    D = D  # Diameter (m)
    L = length  # Length (m)
    k = k  # Relative roughness   (m)
    dens = dens  # Density  (kg/m³)
    viscosity = viscosity  # Viscosity (kg/(s*m))

    def colebrook(x, R):
        F = ((1 / math.sqrt(x)) + 2 * math.log((k / (3.7 * D)) + (2.51 / (R * math.sqrt(x))), 10))
        return F

    def derivative(x, R):
        F_dash = (-1 / 2 * (x ** (-3 / 2)) * (1 + (2.18261 / R) * ((k / 3.7) + (2.51 / (R * math.sqrt(x))) ** -1)))
        return F_dash

    def newtonRaphson(x, R):
        h = colebrook(x, R) / derivative(x, R)
        while abs(h) >= 0.0001:
            h = colebrook(x, R) / derivative(x, R)
            x -= h
        return x

    def secant(_x1, _x2, _E, R):
        n = 0
        if colebrook(_x1, R) * colebrook(_x2, R) != 0:
            while True:
                _x0 = ((_x1 * colebrook(_x2, R) - _x2 * colebrook(_x1, R)) /
                       (colebrook(_x2, R) - colebrook(_x1, R)))
                c = colebrook(_x1, R) * colebrook(_x0, R)
                _x1 = _x2
                _x2 = _x0

                n += 1

                if c == 0:
                    break
                xm = ((_x1 * colebrook(_x2, R) - _x2 * colebrook(_x1, R)) /
                      (colebrook(_x2, R) - colebrook(_x1, R)))

                if abs(xm - _x0) < _E:
                    break

            return _x0

        else:
            print("Can not find a root in ",
                  "the given interval")

    Re = rey

    # constants required for Newton Raphson
    x0 = 64 / 2100

    # iteration for Newton Raphson
    newtonR = []
    for i in range(len(Re)):
        nr = newtonRaphson(x0, Re[i])
        newtonR.append(nr)

    # constants required for Secant Method
    x1 = 24 / 2100
    x2 = 0.0005
    E = 0.0001

    # iteration for Secant Method
    secantM = []
    for i in range(len(Re)):
        sm = secant(x1, x2, E, Re[i])
        secantM.append(sm)

    return newtonR, secantM


def index(request):
    length = request.GET.get('length', 1)
    diameter = request.GET.get('diameter', 0.0254)
    density = request.GET.get('density', 997)
    viscosity = request.GET.get('viscosity', 0.000547)
    rel_rough = request.GET.get('rel_rough', 0.002)
    """ 
    print("Length: ", length)
    print("diameter: ", diameter)
    print("density: ", density)
    print("viscosity: ", viscosity)
    print("rel_rough: ", rel_rough)
    """
    length = float(length)
    diameter = float(diameter)
    density = float(density)
    viscosity = float(viscosity)
    rel_rough = float(rel_rough)
    rey = request.GET.get('text', ' ')
    rey = list(rey)

    reynolds = []
    i = 0
    num = ''
    rey.append(' ')
    while i < len(rey) - 1:
        if rey[i + 1] != ' ':
            num += rey[i]
            i += 1
        else:
            num += rey[i]
            i += 2
            if num != ' ':
                reynolds.append(int(num))
            num = ''
    print(reynolds)

    ff = request.GET.get('text2', ' ')
    ff = list(ff)

    relrough = []
    i = 0
    num = ''
    ff.append(' ')
    while i < len(ff) - 1:
        if ff[i + 1] != ' ':
            num += ff[i]
            i += 1
        else:
            num += ff[i]
            i += 2
            if num != ' ':
                relrough.append(float(num))
            num = ''
    print(relrough)
    new, sec = plot(reynolds, length, diameter, density, viscosity, rel_rough)
    print("Newton Raphson:", new)
    print("Secant Method", sec)
    params = {'rey': reynolds, 'rr': relrough, 'new': new, 'sec': sec, 'length': length, 'diameter': diameter,
              'density': density, 'viscosity': viscosity, 'rel_rough': rel_rough}

    return render(request, 'moody/index.html', params)
