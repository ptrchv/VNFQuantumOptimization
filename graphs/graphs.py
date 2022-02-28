# %%
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
import pandas as pd

# Is it possible to change the markers according to the color?

# Is it clear or do we need to separate those charts?

def qubo_vars_complete():

    headers = ['Nodes', 'SFCs', 'VNFs', 'vars']
    df = pd.read_csv('qubo_vars_variation.csv', names=headers)
    print(df)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlabel("Nodes")
    ax.set_xticks(np.arange(0,40,10))
    ax.set_ylabel("SFCs")
    ax.set_yticks(np.arange(1,7,1))
    ax.set_zlabel("QUBO vars")
    ax.set_zticks(np.arange(0,10000,1500))

    x = df['Nodes']
    y = df['SFCs']
    z = df['vars']
    c = df['VNFs']

    m = ['o','x','j','k','+']

    cmap_custom = mpl.colors.ListedColormap(["navy", "red", "limegreen", "gray", "magenta"])
    norm = mpl.colors.BoundaryNorm(np.arange(1.5,7), cmap_custom.N)

    img = ax.scatter(x, y, z, c=c, cmap=cmap_custom, norm=norm)

    fig.colorbar(img, ticks=np.linspace(2,6,5))
    fig.set_size_inches(18.5,10.5, forward=True)

    plt.savefig("result.png", dpi=200)
    plt.show()

def qubo_vars_node_fixed():

    headers = ['SFCs', 'VNFs', 'vars']
    df = pd.read_csv('qubo_vars_node_fixed.csv', names=headers)
    print(df)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.set_xlabel("SFCs")
    ax.set_xticks(np.arange(0,5,1))
    ax.set_ylabel("VNFs")
    ax.set_yticks(np.arange(1,7,1))
    ax.set_zlabel("QUBO vars")
    ax.set_zticks(np.arange(0,5000,500))

    x = df['SFCs']
    y = df['VNFs']
    z = df['vars']

    img = ax.bar3d(x, y, z)

    fig.set_size_inches(18.5,10.5, forward=True)

    plt.savefig("result.png", dpi=200)
    plt.show()

def test():
    headers = ['Nodes', 'SFCs', 'VNFs', 'vars']
    df = pd.read_csv('qubo_vars_variation.csv', names=headers)
    print(df)

    x = df['Nodes']
    y = df['VNFs']    
    z = df['vars']
    c = df['SFCs']         

    # convert to 2d matrices
    Z = np.outer(z.T, z)  
    X, Y = np.meshgrid(x, y)
    C = np.outer(c.T, c)   

    # fourth dimention - colormap
    # create colormap according to x-value (can use any 50x50 array)
    color_dimension = C # change to desired fourth dimension
    minn, maxx = color_dimension.min(), color_dimension.max()
    norm = mpl.colors.Normalize(minn, maxx)
    m = plt.cm.ScalarMappable(norm=norm, cmap='jet')
    m.set_array([])
    fcolors = m.to_rgba(color_dimension)

    # plot
    fig = plt.figure()
    ax = fig.gca(projection='3d')
    img = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, facecolors=fcolors, vmin=minn, vmax=maxx, shade=False)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    fig.colorbar(img)
    fig.set_size_inches(18.5,10.5, forward=True)
    fig.canvas.show()

def test2():
    headers = ['SFCs', 'VNFs', 'vars']
    df = pd.read_csv('qubo_vars_node_fixed.csv', names=headers)
    print(df)

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.set_xlabel("SFCs")
    ax.set_xticks(np.arange(0,5,1))
    ax.set_ylabel("VNFs")
    ax.set_yticks(np.arange(1,7,1))
    ax.set_zlabel("QUBO vars")
    ax.set_zticks(np.arange(0,5000,1000))

    x = df['SFCs']
    y = df['VNFs']
    z = df['vars']

    Z = np.outer(z.T,z)
    X, Y = np.meshgrid(x,y)

    ax.plot_surface(X,Y,Z, shade=False, antialiased=True)

    fig.set_size_inches(18.5,10.5, forward=True)

    plt.savefig("result.png", dpi=200)
    plt.show()


#qubo_vars_node_fixed()
qubo_vars_complete()


# %%
