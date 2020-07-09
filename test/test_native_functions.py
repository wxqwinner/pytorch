from typing import Optional, List
import torch
from torch.testing._internal.common_utils import TestCase

# End-to-end tests of features in native_functions.yaml

class IntListWrapperModule(torch.nn.Module):
    def forward(self, values, incr: Optional[List[int]]):
        return torch._C._nn._test_optional_intlist(values, incr)


class TestNativeFunctions(TestCase):

    def do_test_optional_intlist_with_module(self, module):
        values = torch.tensor([1, 2], dtype=torch.int)

        returned = module(values, None)
        self.assertEqual(values, returned)
        # Make sure that it's an alias, indicating that the operator saw a nullopt.
        values[0] = 3
        self.assertEqual(values, returned)

        returned = module(values, [5, 4])
        self.assertEqual(values, torch.tensor([3, 2], dtype=torch.int))
        self.assertEqual(returned, torch.tensor([8, 6], dtype=torch.int))

    def trace_optional_intlist(self, const):
        def wrapper(values):
            return torch._C._nn._test_optional_intlist(values, const)
        return torch.jit.trace(wrapper, torch.tensor([1, 2], dtype=torch.int))

    def test_optional_intlist(self):
        self.do_test_optional_intlist_with_module(IntListWrapperModule())
        self.do_test_optional_intlist_with_module(torch.jit.script(IntListWrapperModule()))

        traced_none = self.trace_optional_intlist(None)
        traced_list = self.trace_optional_intlist([5, 4])

        # Not really a module, just lets us use our two traced functions to handle
        # the specific cases of passing None and [5, 4].
        def fake_module(values, const):
            if const is None:
                return traced_none(values)
            if const == [5, 4]:
                return traced_list(values)
            raise Exception("Invalid argument")

        self.do_test_optional_intlist_with_module(fake_module)

    def test_optional_intlist_invalid(self):
        with self.assertRaisesRegex(TypeError, "must be .* but found"):
            IntListWrapperModule()(torch.zeros(1), [0.5])

        with self.assertRaisesRegex(RuntimeError, "value of type .* instead found type"):
            torch.jit.script(IntListWrapperModule())(torch.zeros(1), [0.5])

        with self.assertRaisesRegex(TypeError, "must be .* Tensor"):
            IntListWrapperModule()(torch.zeros(1), torch.zeros(1))

        with self.assertRaisesRegex(RuntimeError, "value of type .* instead found type"):
            torch.jit.script(IntListWrapperModule())(torch.zeros(1), torch.zeros(1))
