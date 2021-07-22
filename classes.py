import numpy as np

class Grid:
    def __init__(self, length, disp_decay, ecol_distr, seed_ecol=1859, seed_biol=376, n_spawn=10):
        self.length = length
        self.disp_decay = disp_decay

        self.all_cells = []
        for i in range(self.length):
            for j in range(self.length):
                self.all_cells.append((i, j))

        # init ecol
        np.random.seed(seed_ecol)
        if ecol_distr == "random_uniform":
            self.ecol = np.random.random((self.length, self.length))
        elif ecol_distr == "random_binary":
            self.ecol = np.random.binomial(1,0.5,(self.length, self.length))
        else:
            raise Exception(f"unexpected type of ecol distribution specified: {ecol_distr}")

        # init biol
        np.random.seed(seed_biol)
        self.biol = np.zeros(self.ecol.shape)
        # spawn initial occurring spots
        for i in range(n_spawn):
            p = self.random_pos()
            self.biol[p[0], p[1]] = 1

        # init reproductive potential
        self.reproduction = np.full(self.ecol.shape, np.nan)

    def step(self, bernoulli):
        # calc reproductive potential per cell:  reproduction_ij = biol_ij*ecol_ij   # fitness(ecol_ij)
        for i, j in self.all_cells:
            self.reproduction[i, j] = self.biol[i, j] * self.ecol[i, j]  # fitness_fxn(self.ecol[i, j], fit=self.fitness_type)

        # disperse
        # for each cell: add decayed reproductive potential to all cells (incl. self)
        biol_NEW = np.zeros(shape=self.biol.shape)
        # TODO: loop in parallel?
        for i, j in self.all_cells:
            for p, q in self.neighbours(i, j):  # considering only moore k-neighbours
                                                # => considerable speed up for larger grids
                biol_NEW[p, q] \
                    += self.reproduction[i, j] * 1 / np.power((1 + self.distance(i, j, p, q)), self.disp_decay)

        # update
        self.biol = np.clip(biol_NEW, a_min=0, a_max=1)
        # bernoulli sampling: ^= simulating population with each grid having a carrying capacity of 1 individual
        # => stochasticity
        if bernoulli:
            self.biol = np.random.binomial(1, self.biol)  # bernoulli sampling for stochastic component


    ### general auxiliary functions:

    def random_pos(self):
        return np.random.randint(self.length, size=2)

    def distance(self, i, j, p, q):
        return np.linalg.norm(np.array([i, j]) - np.array([p, q]))

    def neighbours(self, i, j, k=5):
        # for a large enough decay exponent: considering neighbors beyond 4 or 5 becomes ~negligible
        neigh = k  # moore neighbourhood
        i_low = np.clip(i - neigh, 0, self.length)
        i_high = np.clip(i + neigh + 1, 0, self.length)  # +1 bc range(a, b+1) -> a, .., b
        j_low = np.clip(j - neigh, 0, self.length)
        j_high = np.clip(j + neigh + 1, 0, self.length)
        neighbours = []
        for i_new in range(i_low, i_high):
            for j_new in range(j_low, j_high):
                neighbours.append((i_new, j_new))
        return neighbours