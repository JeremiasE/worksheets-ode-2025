import sympy
from sympy import sin, cos, exp
from sympy.utilities import lambdify
import ipywidgets as widgets
import urllib.parse
from sympy.printing.glsl import GLSLPrinter
from sympy.core import Basic, S
from sympy.core.function import Lambda
from sympy.plotting.plot import Line2DBaseSeries
from sympy.plotting.plot import Plot
from sympy import sympify, Expr, Function
from sympy.plotting.plot import check_arguments, flat
from sympy.external import import_module
from matplotlib import colors

from sympy.printing.codeprinter import CodePrinter
from sympy.printing.precedence import precedence
from sympy.core.mul import _keep_coeff
from sympy.core import Add, Mul, Pow, S, sympify, Float
from sympy.printing.precedence import precedence, PRECEDENCE

import numpy as np
import matplotlib.pyplot as plt
import scipy
import scipy.integrate


# we have to monkey patch 

def _new_print_Pow(self, expr):
    PREC = precedence(expr)
    if expr.exp == -1:
        return '1.0/%s' % (self.parenthesize(expr.base, PREC))
    elif expr.exp == 0.5:
         return 'sqrt(%s)' % self._print(expr.base)
    
    else:
        try:
            e = self._print(float(expr.exp))
        except TypeError:
            e = self._print(expr.exp)
        if expr.exp.is_Integer and expr.exp>=0:
            if expr.exp%2 == 0:
                 return self._print_Function_with_args('pow', (
                 self._print(abs(expr.base)),
                 e
            ))
            else:
                return (self._print_Function_with_args('sign', (
                     self._print(expr.base)))+"*"+
                     self._print_Function_with_args('pow', (
                     self._print(abs(expr.base)),
                     e
                )))
            
        return self._print_Function_with_args('pow', (
            self._print(expr.base),
            e
        ))


def _new_print_Mul(self, expr):
        prec = precedence(expr)

        c, e = expr.as_coeff_Mul()
        if c < 0:
            expr = _keep_coeff(-c, e)
            sign = "-"
        else:
            sign = ""

        a = []  # items in the numerator
        b = []  # items that are in the denominator (if any)

        pow_paren = []  # Will collect all pow with more than one base element and exp = -1

        if self.order not in ('old', 'none'):
            args = expr.as_ordered_factors()
        else:
            # use make_args in case expr was something like -x -> x
            args = Mul.make_args(expr)

        # Gather args for numerator/denominator
        for item in args:
            if item.is_commutative and item.is_Pow and item.exp.is_Rational and item.exp.is_negative:
                if item.exp != -1:
                    b.append(Pow(item.base, -item.exp, evaluate=False))
                else:
                    if len(item.args[0].args) != 1 and isinstance(item.base, Mul):   # To avoid situations like #14160
                        pow_paren.append(item)
                    b.append(Pow(item.base, -item.exp))
            else:
                a.append(item)

        a = a or [1.0] # There is a bug here

        if len(a) == 1 and sign == "-":
            # Unary minus does not have a SymPy class, and hence there's no
            # precedence weight associated with it, Python's unary minus has
            # an operator precedence between multiplication and exponentiation,
            # so we use this to compute a weight.
            a_str = [self.parenthesize(a[0], 0.5*(PRECEDENCE["Pow"]+PRECEDENCE["Mul"]))]
        else:
            a_str = [self.parenthesize(x, prec) for x in a]
        b_str = [self.parenthesize(x, prec) for x in b]

        # To parenthesize Pow with exp = -1 and having more than one Symbol
        for item in pow_paren:
            if item.base in b:
                b_str[b.index(item.base)] = "(%s)" % b_str[b.index(item.base)]

        if not b:
            return sign + '*'.join(a_str)
        elif len(b) == 1:
            return sign + '*'.join(a_str) + "/" + b_str[0]
        else:
            return sign + '*'.join(a_str) + "/(%s)" % '*'.join(b_str)

GLSLPrinter._print_Pow = _new_print_Pow
GLSLPrinter._print_Mul = _new_print_Mul


GLSLPrinter._print_Pow = _new_print_Pow

def to_glsl(expr,assign_to=None,**settings):
    p = GLSLPrinter(settings)
    return str(p.doprint(expr,assign_to))

def field_player(f,width=1300,height=700):
    code = f"""vec2 get_velocity(vec2 p) {{
    vec2 v = vec2(0., 0.);
    float x = p.x;
    float y = p.y;
    v.x = {to_glsl(sympy.N(f[0]))};
    v.y = {to_glsl(sympy.N(f[1]))};
    return v;
    }}"""
    out = widgets.Output(layout={'border': '1px solid black'})
    from IPython.display import IFrame
    url = 'https://anvaka.github.io/fieldplay/?cx=0.0017000000000000348&cy=0&w=8.543199999999999&h=8.543199999999999&dt=0.01&fo=0.998&dp=0.009&cm=1'+'&vf='+urllib.parse.quote(code)
    return IFrame(url, width=width, height=height)


def plot_vector_field(g,var1,var2, numpoints=20, ax=None, **args):
    X,Y = np.meshgrid(np.linspace(var1[1],var1[2],numpoints), np.linspace(var2[1],var2[2],numpoints))

    f1 = lambdify([var1[0], var2[0]], g[0])
    f2 = lambdify([var1[0], var2[0]], g[1])

    U = np.vectorize(f1)(X,Y)
    V = np.vectorize(f2)(X,Y)

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
    ax.set_xlim(var1[1],var1[2])
    ax.set_ylim(var2[1],var2[2])
    ax.quiver(X,Y,U,V, angles='xy',**args)
    return ax

def add_central_axis(ax):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    ax.hlines(0,xmin,xmax,color="black")
    ax.vlines(0,ymin,ymax,color="black")
    return ax
    

def plot_streamlines(g,var1,var2,numpoints=100, ax=None, **args):
    X,Y = np.meshgrid(np.linspace(var1[1],var1[2],numpoints), np.linspace(var2[1],var2[2],numpoints))

    f1 = lambdify([var1[0], var2[0]], g[0])
    f2 = lambdify([var1[0], var2[0]], g[1])

    U = np.vectorize(f1)(X,Y)
    V = np.vectorize(f2)(X,Y)

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
    #ax.spines['left'].set_position('center')
    #ax.spines['bottom'].set_position('center')
    #ax.spines['right'].set_color('none')
    #ax.spines['top'].set_color('none')
    ax.set_xlim(var1[1],var1[2])
    ax.set_ylim(var2[1],var2[2])
    ax.streamplot(X,Y,U,V,**args)
    #ax.legend(loc=1)
    return ax

def plot_contour(g,var1,var2,numpoints=100, ax=None, filled=True, **args):
    X,Y = np.meshgrid(np.linspace(var1[1],var1[2],numpoints), np.linspace(var2[1],var2[2],numpoints))

    f = lambdify([var1[0], var2[0]], g)

    Z = np.vectorize(f)(X,Y)

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
    #ax.spines['left'].set_position('center')
    #ax.spines['bottom'].set_position('center')
    #ax.spines['right'].set_color('none')
    #ax.spines['top'].set_color('none')
    ax.set_xlim(var1[1],var1[2])
    ax.set_ylim(var2[1],var2[2])
    c = None
    if filled:
        c = ax.contourf(X,Y,Z,**args)
    else:
        c= ax.contour(X,Y,Z,**args)
    #ax.legend(loc=1)
    return ax, c 

def solve_ivp(f,variables,t_range,initial_value,max_step=0.1):
    f1 = lambdify(variables, f[0])
    f2 = lambdify(variables, f[1])
    def right_hand_side(t,y):
        return (f1(y[0],y[1]),f2(y[0],y[1]))
    solution = scipy.integrate.solve_ivp(right_hand_side, t_range,initial_value, dense_output=True, max_step=0.1)
    return solution

def solve_non_autonomous_ivp(f,time_var, space_vars,t_range,initial_value,max_step=0.1):
    f1 = lambdify([time_var]+list(space_vars), f[0])
    f2 = lambdify([time_var]+list(space_vars), f[1])
    def right_hand_side(t,y):
        return (f1(t,y[0],y[1]),f2(t,y[0],y[1]))
    solution = scipy.integrate.solve_ivp(right_hand_side, t_range,initial_value, max_step=0.1)
    return solution


def plot_solution_pair(f,variables,t1=18.0,x_0=0.2,y_0=0):
    fig = plt.figure()
    (ax1,ax2) = fig.subplots(1,2)
    solution = solve_ivp(f,variables,(0,t1),(x_0,y_0))
    ax1.plot(solution.t,solution.y[0,:])
    ax2.plot(solution.t,solution.y[1,:],color="red")
    return fig

def plot_solution_non_autonomous(f, time_var, space_vars,initial_value, t_1=12):
    solution = solve_non_autonomous_ivp(f,time_var, space_vars,(0,t_1),initial_value)
    fig = plt.figure()
    ax = fig.subplots(1,1)
    ax.plot(solution.t,solution.y[0,:])
    fig.set_figwidth(16)
    fig.set_figheight(5)
    return fig

def norm(f):
    return sympy.sqrt((f.T@f)[0])


def plot(f, xtuple, ylimits=None, numpoints=3000, ax=None, detect_poles = True, eps=0.01,**kwargs):
    (x, xmin, xmax) = xtuple
    f1 = lambdify(x, f)
    X = np.linspace(xmin,xmax,numpoints)
    Y = np.vectorize(f1)(X)
    if detect_poles:
        X, Y = _detect_poles_helper(X,Y,eps)

    if ax is None:
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)

    ax.set_xlim(xmin,xmax)
    if ylimits:
        ax.set_ylim(*ylimits)
    else:
        ax.set_ylim(min(Y),max(Y))

    ax.plot(X,Y,**kwargs)
    
    return ax

# This is taken from sympy plotting backend 
def _detect_poles_helper(x, y, eps=0.01):
    """Compute the steepness of each segment. If it's greater than a
    threshold, set the right-point y-value non NaN.
    """
    np = import_module('numpy')

    yy = y.copy()
    threshold = np.pi / 2 - eps
    for i in range(len(x) - 1):
        dx = x[i + 1] - x[i]
        dy = abs(y[i + 1] - y[i])
        angle = np.arctan(dy / dx)
        if abs(angle) >= threshold:
            yy[i + 1] = np.nan
    return x, yy

def plot_slope_field(g,var1,var2, numpoints=20, ax=None, pivot="middle", **kwargs):
    norm_inverse = 1 / sympy.sqrt((g**2+1))
    g_normalized = g * norm_inverse
    return plot_vector_field(
        sympy.Matrix((norm_inverse,g_normalized)),var1,var2, 
        numpoints=numpoints, 
        ax = ax, 
        headwidth = 0, 
        headlength = 0, 
        headaxislength = 0,
        pivot = pivot, 
        **kwargs)

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap
