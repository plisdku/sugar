#include <iostream>
#include <cstdint>
#include <cstdlib>
#include <stdexcept>

#include <Eigen/Core>

#include "sugar.h"

void initialize()
{
}

double sum_double_np_array(double* a, int n)
{
    Eigen::Map<Eigen::VectorXd> x(a,n);
    return x.sum();
}


