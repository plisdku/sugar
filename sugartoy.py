import numpy as np

import sugar



def main():
    print("HI!")
    sugar.initialize()

    y = sugar.sugar_sum(np.arange(10.0))
    print("y =", y)




if __name__ == "__main__":
    main()


