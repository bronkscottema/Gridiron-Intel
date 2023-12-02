import os

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as font_manager
from matplotlib import rcParams

pd_options = {
'display.max_columns' : 100,
}
[pd.set_option(option, setting) for option, setting in pd_options.items()]

font_dirs = ['C:\\Users\\bronkscottema\\Desktop\\Development\\Audible_Analytics\\fonts\\']
for font in font_manager.findSystemFonts(font_dirs):
    font_manager.fontManager.addfont(font)
plt.rcParams['font.family'] = 'Besley-Bold'

def create_football_field(linenumbers=True,
                          endzones=True,
                          highlight_line=False,
                          highlight_line_number=50,
                          highlighted_name='Line of Scrimmage',
                          fifty_is_los=False,
                          figsize=(7, 10)):
    """
    Function that plots the football field for viewing plays.
    Allows for showing or hiding endzones.
    """
    rect = patches.Rectangle((0, 0), 53.3, 120, linewidth=0.1,
                             edgecolor='white', facecolor='green', zorder=0)

    fig, ax = plt.subplots(1, figsize=figsize)
    ax.add_patch(rect)

    plt.plot( [0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0,
              0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0,
              0, 53.3, 0, 0, 53.3, 0, 0, 53.3, 0],
              [10, 10, 10, 15, 15, 15, 20, 20, 20, 25, 25, 25, 30, 30, 30, 35, 35, 35, 40, 40, 40, 45, 45, 45, 50, 50, 50,
              55, 55, 55, 60, 60, 60, 65, 65, 65, 70, 70, 70, 75, 75, 75, 80, 80, 80, 85, 85, 85, 90, 90, 90, 95, 95, 95,
              100, 100, 100, 105, 105, 105, 110, 110, 110],
             color='white')
    # Endzones
    if endzones:
        ez1 = patches.Rectangle((0, 0), 53.3, 10,
                                linewidth=0.1,
                                edgecolor='white',
                                facecolor='white',
                                alpha=0.2,
                                zorder=0)
        ez2 = patches.Rectangle((0, 110), 53.3, 120,
                                linewidth=0.1,
                                edgecolor='white',
                                facecolor='white',
                                alpha=0.2,
                                zorder=0)
        ax.add_patch(ez1)
        ax.add_patch(ez2)
    plt.ylim(0, 120)
    plt.xlim(-5, 58.3)
    plt.axis('off')
    if linenumbers:
        for x in range(20, 110, 10):
            numb = x
            if x > 50:
                numb = 120 - x
            #10 yard line
            if numb - 10 == 10:
                plt.text(12, x - 1.1, str(numb - 10).replace("", " "),
                         horizontalalignment='center',
                         fontsize=19, fontname='Besley-Bold',
                         color='white', rotation=90)
                plt.text(53.3 - 12, x - 1.1, str(numb - 10).replace("", " "),
                         horizontalalignment='center',
                         fontsize=19, fontname='Besley-Bold',
                         color='white', rotation=90)
            elif numb - 10 == 30:
                plt.text(12, x - 1.1, str(numb - 10).replace("", " "),
                         horizontalalignment='center',
                         fontsize=19, fontname='Besley-Bold',
                         color='white', rotation=90)
                plt.text(53.3 - 12, x - 1.1, str(numb - 10).replace("", " "),
                         horizontalalignment='center',
                         fontsize=19, fontname='Besley-Bold',
                         color='white', rotation=90)
            elif numb - 10 == 40:
                plt.text(12, x - 1.1, str(numb - 10).replace("", " "),
                         horizontalalignment='center',
                         fontsize=19, fontname='Besley-Bold',
                         color='white', rotation=90)
                plt.text(53.3 - 12, x - 1.1, str(numb - 10).replace("", " "),
                         horizontalalignment='center',
                         fontsize=19, fontname='Besley-Bold',
                         color='white', rotation=90)
            else:
                plt.text(12, x - 1, str(numb - 10).replace("", " "),
                         horizontalalignment='center',
                         fontsize=19, fontname='Besley-Bold',
                         color='white', rotation=90)
                plt.text(53.3 - 12, x - 1, str(numb - 10).replace("", " "),
                         horizontalalignment='center',
                         fontsize=19, fontname='Besley-Bold',
                         color='white', rotation=90)

    if endzones:
        hash_range = range(11, 110)
    else:
        hash_range = range(1, 120)

    for x in hash_range:
        #NFL
        # ax.plot([0.4, 0.7], [x,x], color='white')
        # ax.plot([53.0, 52.5], [x,x], color='white')
        # ax.plot([23.33, 24.00], [x,x], color='white')
        # ax.plot([29.33, 30.00], [x,x], color='white')
        #COLLEGE
        ax.plot([0.4, 0.7], [x, x], color='white')
        ax.plot([53.0, 52.5], [x, x], color='white')
        ax.plot([20.00, 20.66], [x, x], color='white')
        ax.plot([32.66, 33.33], [x, x], color='white')

    if highlight_line:
        hl = highlight_line_number + 10
        plt.plot([hl, hl], [0, 53.3], color='white')
        plt.text(hl + 2, 50, '<- {}'.format(highlighted_name),
                 color='white')
    return fig, ax

create_football_field()
plt.gca().set_axis_off()
plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0,
            hspace = 0, wspace = 0)
plt.margins(0,0)
plt.gca().xaxis.set_major_locator(plt.NullLocator())
plt.gca().yaxis.set_major_locator(plt.NullLocator())
plt.savefig("filename.pdf", bbox_inches = 'tight',
    pad_inches = 0)
plt.show()
#NFL not zoomed in
# if numb - 10 == 10:
#     plt.text(12, x - 2, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 12, x - 2, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     # 40
# elif numb - 10 == 40:
#     plt.text(12, x - 2.7, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 12, x - 2.7, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
# else:
#     plt.text(12, x - 2.5, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 12, x - 2.5, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
# NFL Zoomed IN

# # NCAA not zoomed in
# if numb - 10 == 10:
#     plt.text(7, x - 2, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 7, x - 2, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     # 40
# elif numb - 10 == 40:
#     plt.text(7, x - 2.7, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 7, x - 2.7, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
# else:
#     plt.text(7, x - 2.5, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 7, x - 2.5, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#NCAA ZOOMED IN
# if numb - 10 == 10:
#     plt.text(12, x - .75, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 12, x - .75, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
# elif numb - 10 == 30:
#     plt.text(12, x - 1.1, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 12, x - 1.1, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
# elif numb - 10 == 40:
#     plt.text(12, x - 1.1, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 12, x - 1.1, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
# else:
#     plt.text(12, x - 1, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)
#     plt.text(53.3 - 12, x - 1, str(numb - 10).replace("", " "),
#              horizontalalignment='center',
#              fontsize=19, fontname='Besley-Bold',
#              color='white', rotation=90)