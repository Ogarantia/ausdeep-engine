# see code in https://math.stackexchange.com/questions/1103399/alternative-quaternion-multiplication-method
import tensorflow as tf
from . import custom_ops


def multiply_by_a1(vector):
  """12 additions
  """
  A = [[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]]

  output_vector = []
  for i in range(4):
    for j in range(4):
      if j == 0:
        if A[i][j] == 1:
          output_vector.append(vector[j])
        else:
          output_vector.append(-vector[j])
      else:
        if A[i][j] == 1:
          output_vector[i] = output_vector[i] + vector[j]
        else:
          output_vector[i] = output_vector[i] - vector[j]
  return output_vector


def multiply_by_a2(vector):
  """8 addtions
  """
  a_plus_b = vector[0] + vector[1]
  a_minus_b = vector[0] - vector[1]
  c_plus_d = vector[2] + vector[3]
  c_minus_d = vector[2] - vector[3]

  return [a_plus_b + c_plus_d,
          a_minus_b + c_minus_d,
          a_plus_b - c_plus_d,
          a_minus_b - c_minus_d]


def quaternion_mult1(tf_op, inputs, kernels, f=1):
  """[summary]

  Args:
      tf_op ([type]): function taking as parameter (input, kernel)
      input ([type]): [description]
      kernel ([type]): [description]
  """
  kernels = [k * f for k in kernels]
  if len(inputs) == 4:
    kernel_sum = multiply_by_a2(kernels)
    input_sum = multiply_by_a2(inputs)
    output_sum = []
    for i in range(4):
      output_sum.append(tf_op(input_sum[i], kernel_sum[i]))
    output_sum = multiply_by_a2(output_sum)

    # other convolution
    output_rest = [
        tf_op(inputs[0], kernels[0]),
        tf_op(inputs[3], kernels[2]),
        tf_op(inputs[1], kernels[3]),
        tf_op(inputs[2], kernels[1]),
    ]

    outputs = [(output_sum[i]/4 - 2*output_rest[i])*(1/f) for i in range(4)]
    outputs[0] = -outputs[0]
  else:
    outputs = [tf_op(inputs[0], kernels[i]) * (1/f) for i in range(4)]
  return outputs


def quaternion_mult2(tf_op, inputs, kernels, f=1):
  kernels = [k * f for k in kernels]
  if len(inputs) == 4:
    k1 = kernels[1] + kernels[2]
    k3 = kernels[0] + kernels[3]
    k4 = kernels[0] - kernels[3]
    k5 = kernels[1] - kernels[2]
    i1 = inputs[3] + inputs[1]
    i3 = inputs[0] - inputs[2]
    i4 = inputs[0] + inputs[2]
    i5 = inputs[3] - inputs[1]
    a1 = tf_op(i1, k1)
    a3 = tf_op(i3, k3)
    a4 = tf_op(i4, k4)
    a2 = a1 + a3 + a4
    a5 = 0.5*(a2 + tf_op(i5, k5))

    k1 = kernels[2] - kernels[3]
    k2 = kernels[1] + kernels[0]
    k3 = kernels[2] + kernels[3]
    k4 = kernels[0] - kernels[1]
    i1 = inputs[3] - inputs[2]
    i2 = inputs[1] + inputs[0]
    i3 = inputs[0] - inputs[1]
    i4 = inputs[3] + inputs[2]

    q1 = a5 - a1 + tf_op(i1, k1)
    q2 = a5 - a2 + tf_op(i2, k2)
    q3 = a5 - a3 + tf_op(i3, k3)
    q4 = a5 - a4 + tf_op(i4, k4)
    return [q1 * (1/f), q2 * (1/f), q3 * (1/f), q4 * (1/f)]
  else:
    outputs = [tf_op(inputs[0], kernels[i]) * (1/f) for i in range(4)]
  return outputs


def quaternion_mult_cpp(tf_op, inputs, kernels, f=1):
  if f != 1:
    kernels = [k * f for k in kernels]
  if len(inputs) != 4:
    output = [tf_op(inputs[0], kernels[i]) for i in range(4)]
    if f != 1:
      output = [o * (1/f) for o in output]
    return output
  inputs_p = custom_ops.upstride_inputs(*inputs)
  kernels_p = custom_ops.upstride_kernels(*kernels)
  outputs_p = [tf_op(inputs_p[i], kernels_p[i]) for i in range(8)]
  outputs = custom_ops.upstride_outputs(*outputs_p)
  if f != 1:
    outputs = [o * (1/f) for o in outputs]
  return outputs


def quaternion_mult_naive(tf_op, inputs, kernels):
  # FIXME: context
  # From the fact that the quaternion product is not commutative (p*q != q*p), the previous
  # implementation commentedout hereafter doesn't lead to the same results as the algorithm
  # generalized for all upstride datatypes in generic_layers.py

  # FIXME: open question
  # Having in mind that the following alternatives are the commutative of each other, which of the
  # them is the expected behavior?

  ## The implementation that differs from generic_layers.py:
  ## c1 = tf_op(inputs[0], kernels[0]) - tf_op(inputs[1], kernels[1]) - tf_op(inputs[2], kernels[2]) - tf_op(inputs[3], kernels[3])
  ## c2 = tf_op(inputs[1], kernels[0]) + tf_op(inputs[0], kernels[1]) - tf_op(inputs[3], kernels[2]) + tf_op(inputs[2], kernels[3])
  ## c3 = tf_op(inputs[2], kernels[0]) + tf_op(inputs[3], kernels[1]) + tf_op(inputs[0], kernels[2]) - tf_op(inputs[1], kernels[3])
  ## c4 = tf_op(inputs[3], kernels[0]) - tf_op(inputs[2], kernels[1]) + tf_op(inputs[1], kernels[2]) + tf_op(inputs[0], kernels[3])

  # The implementation that behaves as generic_layers.py
  c1 = tf_op(inputs[0], kernels[0]) - tf_op(inputs[1], kernels[1]) - tf_op(inputs[2], kernels[2]) - tf_op(inputs[3], kernels[3])
  c2 = tf_op(inputs[1], kernels[0]) + tf_op(inputs[0], kernels[1]) + tf_op(inputs[3], kernels[2]) - tf_op(inputs[2], kernels[3])
  c3 = tf_op(inputs[2], kernels[0]) - tf_op(inputs[3], kernels[1]) + tf_op(inputs[0], kernels[2]) + tf_op(inputs[1], kernels[3])
  c4 = tf_op(inputs[3], kernels[0]) + tf_op(inputs[2], kernels[1]) - tf_op(inputs[1], kernels[2]) + tf_op(inputs[0], kernels[3])
  return [c1, c2, c3, c4]


def quaternion_mult_conv(tf_op, inputs, kernels, channel_axis):
  """ Special version for the convolution. It use the group convolution instead of calling 8 times the convolution
  """
  if len(inputs) != 4:
    # basic version is output = [tf_op(inputs[0], kernels[i]) for i in range(4)]
    # but here we can concatenate the 4 kernel and do a single convolution
    # kernel have shape (h,w,input,output)
    kernel = tf.concat(kernels, axis=3)
    output = tf_op(inputs[0], kernel)
    outputs = tf.split(output, num_or_size_splits=4, axis=channel_axis)
    return outputs
  inputs_p = custom_ops.upstride_inputs(*inputs)
  kernels_p = custom_ops.upstride_kernels(*kernels)
  # instead of calling outputs_p = [tf_op(inputs_p[i], kernels_p[i]) for i in range(8)]
  # we can use group convolution
  kernel_p = tf.concat(kernels_p, axis=3)
  input_p = tf.concat(inputs_p, axis=channel_axis)
  output_p = tf_op(input_p, kernel_p)
  outputs_p = tf.split(output_p, num_or_size_splits=8, axis=channel_axis)
  outputs = custom_ops.upstride_outputs(*outputs_p)
  return outputs


multiply_by_a = multiply_by_a1
# mult 2 is more stable than mult 1 when working with float 16
quaternion_mult = quaternion_mult_naive


def is_quaternion_init(init_type):
  """
  Determine whether it is a quaternion initialization or not
  Args:
      init_type: str or tf.keras.initializers.Initializer, initialization type for upstride quaternion, either
      'up2_init_he'  or 'up2_init_glorot' for real valued initialization should be tensorflow
  """

  if isinstance(init_type, str) and 'up2_init' in init_type:
    return True

  return False
