# CS50AI
CS50 AI coursework

At first run, I used 
1 convolutional layer with 32 filters and a 3x3 kernel + ReLu activation function,
1 max pooling layer with a pool size of 2x2, and
1 hidden layer with 128 units(neurons) and a dropout of 0.5 + ReLu activation function
<br>
It took around 8 seconds each epoch
and the results yielded a loss of 2.2317, and an accuracy: 0.3311 
<br>
<br>
I had very poor results and the first variable I wanted to change was the number of convolutional and max-pool layers.
Keeping everything else constant, I started to increase the number of convolutional and max-pool layers and attained these results:

| Convolutional + Maxpool Layers | 1      | 2      |  3     |
| :---:                          | :---:  | :---:  | :---:  |
| Loss                           | 2.2317 | 0.2361 | 0.1827 |
| Accuracy                       | 0.3311 | 0.9357 | 0.9535 |
| Time each epoch                | 8 .0   | 7.1    | 7.4    |
<br>
When trying to use 4 layers of convolution + max pool, I ran into an error saying that the input size could no longer be reduced any further.
<br>
<br>

Inspecting the data, there was a massive spike in accuracy from 1 layer -> 2 layers. So I tested with: <br><br>
1 convolution + maxpool layer followed by a convolutional layer --resulting--> 0.97 accuuracy <br>
1 convolution + maxpool layer followed by a maxpool layer --resulting--> 0.05 accuracy <br><br>

Continuing with 1 convolutional layer with 32 filters and a 3x3 kernel + ReLu activation function,
1 max pooling layer with a pool size of 2x2,
another convolutional layer with 32 filters and a 3x3 kernel + ReLu activation function, and
1 hidden layer with 128 units(neurons) and a dropout of 0.5 + ReLu activation function,
I experimented with the amount of units in the hidden layer and noticed that 128, 256, and 512 yielded very similar accuracies. I kept the 256 units
in the hidden layer and changed the activation function of the first convolutional layer to "sigmoid" to achieve a final accuracy of 0.9832

From playing around with each layer,
I noticed that max pooling + convolution has a very large impact on accuracy when dealing with computer vision.
Using a convolution layer after a max pool layer leads the computer to bettter identify features of a picture.
I also learned that more units in a neural network does not necessarily mean better accuracy. 
To achieve a high accuracy when using these convolutional neural networks, 
it requires knowledge on the input data (the size of each input, distinguishable features, etc),
the effects of adding each layer and understanding how the activation functions changes how the computer deals with the specific numbers in a model.