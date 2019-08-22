import torch



class Block(torch.nn.Module):

    def __init__(self):
        super(Block, self).__init__()


class TeenyGoNetwork(torch.nn.Module):

    # convolutional network
    # outputs 81 positions, 1 pass, 1 win/lose rating
    # residual network

    def __init__(self):

        # inherit class nn.Module
        super(TeenyGoNetwork, self).__init__()

        # define network
        self.num_res_blocks = 20
        self.layers = {}
        self.optimizer = None

        # initilize network
        self.initialize_layers()
        self.initialize_optimizer()

    def predict(self):
        pass

    def initialize_layers(self):

        for i in range(1, self.num_res_blocks+1):
            self.layers["l"+str(i)] = Block()

    def initialize_optimizer(self):
        pass



def main():
    x = torch.randn(100, 9, 9, 20)
    tgn = TeenyGoNetwork()
    tgn.predict(x)

if __name__ == "__main__":
    main()
