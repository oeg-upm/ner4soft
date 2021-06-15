# GNN_GPU
HPCC's GNN with GPU acceleration


## Description
Large neural networks typically train on very large datasets. 
The size of the data combined with the size and complexity of neural networks result in large computational requirements. 
Until now, HPCC Systems is primarily a CPU based system which can result in neural network training times that are impractically long.
With the use of modern GPUs, the training time can be drastically reduced overusing CPUs alone.

This repository consists of a modified GNN bundle and example code showing how it is possible to train large neural networks on multiple GPUs using HPCC Systems. One can train a single NN model across multiple GPUs that span 
multiple physical computers or even onto just one. Choosing how many GPUs to use is up to the developer as each model and dataset are different. Training time performance metrics are provided that demonstrate
the scalability of the setup with respect to training dataset size and neural network size (measured as a number of trainable features).

## Performance

The performance of GPU accelerated GNN was evaluated with a series of experiments, comparing CPU-GNN and GPU-GNN. using 2, 4, 8, and 16 nodes (node is a CPU or GPU) accross two AWS instances (p2.8xlarge) using 9 different combinations of neural network size and training data set sizes. The figure below shows
the average speedup using GPUs over CPUs is shown (the [Experiments](Experiments/data_analysis/graphs/) dir has more granular comparisons). The speedup is how much faster is using a GPU compared to a CPU. The results are averaged between all node sizes. Thus, this graph clearly shows that using GPUs is always faster, but the degree of the speedup is dependent on the NN model size and the data set size.

As you can see from the figure, the speedup for a small NN model, in this case one with 34k trainable parameters, is independent from the dataset size and marginally faster than using a CPU alone. 
Once the model is of sufficient size, you can see the GPUs are significantly faster than CPU alone. It is worth mentioning the GPUs used in these experiments are no longer cutting edge, thus newer, 
faster GPUs will have a larger increase in performance over the CPUs. The case when the model is much larger, the effect of the dataset size is exaggerated. This is likely because the system is at 
this point spending a larger percentage of time performing the expensive calculations as compared to spending time communicating between the nodes.

![Average Speedup](images/speedup.png)


## Getting Started

### Requirements
You must have a compatible NVIDIA GPU for the GPU acceleration to work, however this work consists of performance improvements-for the standard GNN-that can speed up the CPU training as well. The 
scope of this repo is limited to the use of GNN and GPUs though.


There is an AWS AMI that was created that you can use (ami-077ae915aa4f576fe), or you can generate your own with [this](https://github.com/xwang2713/cloud-image-build). 
This produces an image with HPCC Systems Platform Community edition, version 7.10.00 pre-installed as well as all other requirements for this bundle, including CUDA version 10.0. 
The image is designed to run on Amazon's [P2](https://aws.amazon.com/ec2/instance-types/p2/) or [P3](https://aws.amazon.com/ec2/instance-types/p3/) machines.


If you want to create your own instances from scratch, all you need is the latest HPCC systems installed on all nodes and these python packages.


Installation of packages used in the experiments:

```
server install commands:
Downloaded HPCC 7.10.0 files into working directory as *.deb

sudo apt-get update -y
sudo dpkg -i /tmp/*.deb
sudo apt-get install -f 

sudo apt-get update -y
yes | sudo apt-get install python3-pip
yes | sudo -H -u hpcc pip3 install --user pandas h5py


wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1804_10.0.130-1_amd64.deb
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/7fa2af80.pub
sudo apt-get update -y
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1804/x86_64/nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt-get install -y ./nvidia-machine-learning-repo-ubuntu1804_1.0.0-1_amd64.deb
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends nvidia-driver-450
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends cuda-10-0 libcudnn7=7.6.0.64-1+cuda10.0  libcudnn7-dev=7.6.0.64-1+cuda10.0

sudo -H -u hpcc pip3 install --user tensorflow-gpu==1.14 keras
```


### Included Training Data
Included is the MNIST [Dataset](Datasets/data_files) (see [reference](http://yann.lecun.com/exdb/mnist/)) used in in the experiments and examples. Additionally, the script to make
the two larger MNIST datasets (to simulate larger data) is included as a Jupyter notebook.
As you can see from the figure, the speedup for a small NN model, in this case one with 34k trainable parameters, is independent from the dataset size and marginally faster than using a CPU alone. Once the model is of sufficient size, you can see the GPUs are significantly faster than CPU alone. It is worth mentioning the GPUs used in these experiments are no longer cutting edge, thus newer, faster GPUs will have a larger increase in performance over the CPUs.



#### Spraying
Spray in the following way, with appropriate names.

* MNIST: Fixed size = 785
	* Train: mnist::train
	* Test: mnist::test
	* Contains 60k training images
	* ~ 50 MB in size
* Medium MNIST: Fixed size = 785
	* Train: mnist::med::train
	* Test: mnist::med::test
	* Contains 600k training images
	* ~500 MB in size
* Large MNIST: Fixed size = 785
	* Train: mnist::big::train
	* Test: mnist::big::test
	* Contains 6M training images
	* ~ 5GB in size

### Examples
Included in this bundle are some [examples](examples/), found in the examples directory. It is recommended to start with an [MLP trained on MNIST](examples/mnist_mlp.ecl)


The [examples](examples/) include how to properly load the image data from raw pixel values into something GNN can use to train NN models. It uses the above MNIST datasets 
to train three arbitrarily large CNN models on each of the three arbitrarily large image data. The code that was used to generate the experimental results are also provided.





## Author
Robert K.L. Kennedy | Summer 2020 | [GitHub](https://github.com/robertken) | [LinkedIn](https://www.linkedin.com/in/robertken/)



