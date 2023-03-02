import random

def generate_height_map(size, roughness):
    # Initialize the height map with random values
    height_map = [[random.random() for _ in range(size)] for _ in range(size)]
    
    # Generate the terrain by repeatedly applying the diamond-square algorithm
    step_size = size - 1
    while step_size > 1:
        half_step = step_size // 2
        
        # Diamond step
        for x in range(half_step, size, step_size):
            for y in range(half_step, size, step_size):
                avg = (height_map[x-half_step][y-half_step] +
                       height_map[x+half_step][y-half_step] +
                       height_map[x-half_step][y+half_step] +
                       height_map[x+half_step][y+half_step]) / 4
                height_map[x][y] = avg + random.uniform(-1, 1) * roughness
        
        # Square step
        for x in range(0, size, half_step):
            for y in range((x + half_step) % step_size, size, step_size):
                avg = 0
                count = 0
                if x >= half_step:
                    avg += height_map[x-half_step][y]
                    count += 1
                if x + half_step < size:
                    avg += height_map[x+half_step][y]
                    count += 1
                if y >= half_step:
                    avg += height_map[x][y-half_step]
                    count += 1
                if y + half_step < size:
                    avg += height_map[x][y+half_step]
                    count += 1
                height_map[x][y] = avg / count + random.uniform(-1, 1) * roughness
        
        step_size //= 2
        roughness /= 2
    
    return height_map



To use this code, you can call the generate_height_map() function and pass in the desired size and roughness values:
height_map = generate_height_map(256, 1.0)
