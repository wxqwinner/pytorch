#pragma once

#include <torch/nn/options/activation.h>
#include <torch/types.h>

namespace torch {
namespace nn{
namespace functional {

inline Tensor elu(const Tensor& input, const ELUOptions& options) {
  if (options.inplace()) {
    return torch::elu_(const_cast<Tensor&>(input), options.alpha());
  } else {
    return torch::elu(input, options.alpha());
  }
}

} // namespace functional
} // namespace nn
} // namespace torch
