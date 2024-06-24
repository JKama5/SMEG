from sympy import *
from sympy.tensor.array.expressions import ArraySymbol
from sympy.physics.vector import ReferenceFrame
from sympy.vector import CoordSys3D, express

# See:
# Presentation of electromagnetic multichannel data: The
# signal space separation method
# Not sure why we can't obtain this:
# https://arxiv.org/pdf/2305.00572.pdf

theta, phi, x, y, z = symbols ('theta phi x y z', real=True)

# e(r)
Y2_0 = 1 / 4 * sqrt(5 / pi) * (3 * cos(theta) ** 2 - 1)
Y2_1 = - 1 / 2 * sqrt(15 / (2 * pi)) * exp(I * phi) * sin(theta) * cos(theta)
Y2_2 = 1 / 4 * sqrt(15 / (2 * pi)) * exp(2 * I * phi) * (sin(theta) ** 2)

Y2_0 = 2 * Y2_0
Y2_1 = 2 * Y2_1
Y2_2 = 2 * Y2_2

# now converting to vector spherical harmonics
# First e(theta) component
dY2_0 = Derivative(Y2_0, theta, evaluate=True)
dY2_1 = Derivative(Y2_1, theta, evaluate=True)
dY2_2 = Derivative(Y2_2, theta, evaluate=True)

# then e(phi) component
imY2_0 = im(Y2_0) / sin(theta)
imY2_1 = im(Y2_1) / sin(theta)
imY2_2 = im(Y2_2) / sin(theta)

C = CoordSys3D('C')

def sph_to_cart_x(Br, Btheta, Bphi):
    return Br * sin(theta) * cos(phi) + Btheta * cos(theta) * cos(phi) - Bphi * sin(phi)

def sph_to_cart_y(Br, Btheta, Bphi):
    return Br * sin(theta) * sin(phi) + Btheta * cos(theta) * sin(phi) + Bphi * cos(phi)

def sph_to_cart_z(Br, Btheta, Bphi):
    return Br * cos(theta) - Btheta * sin(theta) + 1 * sin(phi)

def sph_to_cart(Br, Btheta, Bphi):
    return (sph_to_cart_x(Br, Btheta, Bphi) * C.x +
            sph_to_cart_y(Br, Btheta, Bphi) * C.y +
            sph_to_cart_z(Br, Btheta, Bphi) * C.z)

S = CoordSys3D('S', variable_names=('r', 'theta', 'phi'))
r = symbols('r', real=True)

B2_0 = r * sph_to_cart(Y2_0, dY2_0, imY2_0).simplify()
# B2_1 = sph_to_cart(Y2_1, dY2_1, imY2_1).simplify()
# B2_2 = sph_to_cart(Y2_2, dY2_2, imY2_2).simplify()

# cart_subs = {theta: atan2(sqrt(x ** 2 + y ** 2 + z ** 2), x),
#              phi: atan2(x, y),
#              r: sqrt(x ** 2 + y ** 2 + z ** 2)}

# B2_0 = r * B2_0.subs(cart_subs)
# B2_0 = B2_0.simplify()
