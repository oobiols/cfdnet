# CFDNet and SURFNet
By: Octavi Obiols-Sales, Abhinav Vishnu, Nicholas Malaya, and [Aparna Chandramowlishwaran](https://hpcforge.eng.uci.edu/).

CFDNet is a deep learning-based accelerator for 2D, coarse-grid, steady-state simulations. SURFNet is an extension of CFDNet, for super-resolution of turbulent flows with transfer learning. SURFNet accelerates fine-grid problems while keeping most data collection at coarse grids.

### CFDNet: accelerating steady-state simulations
CFDNet was published at the International Conference in Supercomputing (2020), and the paper can be found [here](https://dl.acm.org/doi/pdf/10.1145/3392717.3392772?casa_token=2Vx83VWZAWwAAAAA:BauwuqoOjxXcjrpfsI1MwemUxyTb3rIfdLnf1zkUX66YCtUmdUNYWJjqf0TPYAIPDhDRX0YhwQ_0).

![cfdnet](https://user-images.githubusercontent.com/58092961/110775315-a4743200-8213-11eb-9c9a-32fe2c9b4c42.jpg)

We summarize the idea as follows:
1. We start the steady-state simulation as usual, with a user-given initial condition, and let the solver carry K iterations -- K _warmup_ iterations, as we call it. Once we reach this intermidiate state, we create our input representation using the flow variable values at that K iteration.
2. We create the input representation described in the publication and pass it to the CNN. The CNN then infers the steady-state -- which is unconstrained (not physically constrained) and has some approximation error. 
3. We feed the output of the CNN back into the physics solver and let the physics solver drop the residual and satisfy the convergence constraints.

### SURFNet: super-resolution flow network.
The core idea of SURFNet is the same as CFDNet. However, one of the drawbacks of CFDNet is that it keeps the grid size constant between data collection, training, and testing. For example, we collect data at a grid size of 64x256, we train with images of size 64x256, and predict and test for 64x256 domains. If we wished to accelerate simulations at finer grids, we should repeat this process with, for instance, 1024x1024 domains. Nevertheless, data collection and training with such large domain/image sizes is computationally impractical. 

SURFNet overcomes this burden. The idea is to accelerate fine-grid simulations while keeping coarse-grid data collection and training with coarse grid solutions. The key step of SURFNet is to _transfer learn_ the CNN weights calibrated with coarse-grid data to fine-grid datasets, which are 15x smaller than the coarse-grid training datasets. The idea is illustrated here:

![surfnet](https://user-images.githubusercontent.com/58092961/110786602-2fa7f480-8221-11eb-8e25-8ecfa475ccbd.jpg)

# Why you might be interested in this repository
## Dataset generation

We provide the recipe for creating the datasets. All the input-output pairs come from simulation data. We use OpenFOAM as the physics solver to generate the data. Note that the recipe that we provide is amenable to any FV/FE/FD application. The input-output pairs are created as seen

![inputoutput](https://user-images.githubusercontent.com/58092961/110804713-46f0dd00-8235-11eb-9a4d-47740d6218e6.jpg)
:


