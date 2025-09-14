# Executed at: 20250913_212412
# Work directory: ./test_workdir2
#==================================================

import matplotlib.pyplot as plt

# Generate some data
x = list(range(10))
y = [i**2 for i in x]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x, y, label='y = x^2')
plt.title('Quadratic Function')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True)
plt.savefig('quadratic_plot.png')

print("Generated quadratic plot and saved as quadratic_plot.png")