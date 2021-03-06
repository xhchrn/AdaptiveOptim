try:
    import sys
    sys.path.remove("/usr/lib/python3/dist-packages")
except ValueError:
    pass

import numpy as np
import os.path as osp
import matplotlib.pyplot as plt
import matplotlib as mpl


def mk_curve(exp_name='sparse', eps=1e-6, max_iter=600, sym=50, save=None,
             save_dir=".", rm=[]):
    curve_cost = np.load('exps/{}/curve_cost.npy'.format(exp_name)).take(0)
    # curve_cost = np.load('save_exp/{}/curve_cost.npy'.format(exp_name)
    #                      ).take(0)
    layer_lvl = [1, 2, 4, 7, 12, 21, 35, 59, 100]
    c_star = min(min(curve_cost['ista']), min(curve_cost['fista']))-eps
    c_star = min(curve_cost['ista'][-1], curve_cost['fista'][-1])-eps
    c_star = min([np.min(v) for v in curve_cost.values()])

    fig = plt.figure('Curve layer - {}'.format(exp_name))
    fig.clear()
    fig.patch.set_alpha(0)
    ax = fig.add_subplot(1, 1, 1)
    fig.subplots_adjust(bottom=.15, top=.99, right=.99)

    y_max = 0
    markevery = .1
    legend = [[], []]

    for model, name, style in [('linear', 'Linear', '--og'),
                               ('ista', 'ISTA', 'g-'),
                               ('fista', 'FISTA', 'ys-'),
                               ]:
        if model in rm:
            continue
        try:
            cc = np.maximum(curve_cost[model]-c_star, eps)
        except KeyError:
            continue
        y_max = max(y_max, cc[0])
        iters = min(max_iter, len(cc))
        t = range(1, len(cc))
        p, = ax.loglog(t, cc[1:], style, markevery=markevery, label=name)
        legend[0] += [p]
        legend[1] += [name]

    for model, name, style in [('lista', 'L-ISTA', 'bo-'),
                               ('lfista', 'L-FISTA', 'c*-'),
                               ('facto', 'FacNet', 'rd-')]:
        if model in rm:
            continue
        cc = np.maximum(curve_cost[model]-c_star, eps)
        y_max = max(y_max, cc[0])
        ll = layer_lvl[:len(cc)]
        p, = ax.loglog(ll, cc, style, label=name)
        legend[0] += [p]
        legend[1] += [name]

    ax.hlines([eps], 1, max_iter, 'k', '--')

    if len(legend[0]) > 4:
        legend = np.array(legend)[:, [1, 0, 2, 4, 5, 3]]
    ax.legend(legend[0], legend[1], fontsize='xx-large', ncol=2, frameon=False)
    ax.set_xlim((1, max_iter))
    ax.set_ylim((eps/2, sym*y_max))
    ax.set_xlabel('# iteration/layers $q$', fontsize='xx-large')
    ax.set_ylabel('Cost function $F(z^{(q)}) - F(z^*)$', fontsize='xx-large')
    for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize(12)
    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(12)
    plt.tight_layout()
    if save:
        plt.savefig(osp.join(save_dir, '{}.pdf'.format(save)), dpi=150,
                    )  # transparent=True)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser('Make figure')
    parser.add_argument('--exp', type=str, default='sparse.05',
                        help='name of the experience')
    parser.add_argument('--save', type=str, default=None,
                        help='save file for the figure')
    parser.add_argument('--save_dir', type=str,
                        default='../../communications/thesis/figures/lista',
                        help='save file for the figure')
    parser.add_argument('-x', type=int, default=600,
                        help='iteration maximal on the figure')
    parser.add_argument('-y', type=int, default=50,
                        help='scaling factor for y')
    parser.add_argument('--eps', type=float, default=1e-6,
                        help='scaling factor for y')
    parser.add_argument('--rm', nargs='+', type=str, default=[],
                        help='remove some curves from the plot')
    parser.add_argument('--seaborn', action="store_true",
                        help="use seaborn color in the plots")
    parser.add_argument('--noshow', action="store_true",
                        help="use seaborn color in the plots")

    args = parser.parse_args()

    if args.seaborn:
        import seaborn
        seaborn.set_color_codes(palette='deep')
        seaborn.set_style("darkgrid", {
            "axes.facecolor": ".9",
            "figures.facecolor": (1, 1, 0, 0.5)})
        seaborn.despine(left=True, bottom=True)
    mpl.rcParams['figure.figsize'] = [12, 6]
    mk_curve(args.exp, eps=args.eps, max_iter=args.x, sym=args.y,
             save=args.save, save_dir=args.save_dir, rm=args.rm)
    if not args.noshow:
        plt.show()
