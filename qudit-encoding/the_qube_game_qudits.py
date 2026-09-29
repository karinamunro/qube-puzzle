######################################################################
# Note:
# Needs images and perm_matrices_MQT.py

######################################################################

# Packages
from mqt.qudits.compiler.state_compilation.state_preparation import StatePrep
from mqt.qudits.quantum_circuit import QuantumRegister, QuantumCircuit
from mqt.qudits.simulation import MQTQuditProvider
from mqt.qudits.simulation.backends.stochastic_sim import measure_state
import numpy as np
import tkinter as tk
from tkinter import font as tkFont
from tkinter import messagebox
import perm_matrices_MQT as pm
import cmath
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import colour
import sigfig as sf
from fractions import Fraction
import scipy.linalg as spla
from types import NoneType
import os
from pathlib import Path

state_dict = {
    "0000": [690, 300],    "0001": [640, 390],    "0010": [860, 390],    "0011": [810, 300],    "0020": [690, 480],    "0021": [810, 480],
    "0100": [860, 570],    "0101": [810, 660],    "0110": [690, 120],    "0111": [975, 570],    "0120": [525, 210],    "0121": [640, 210],
    "1000": [525, 570],    "1001": [810, 120],    "1010": [690, 660],    "1011": [640, 570],    "1020": [860, 210],    "1021": [975, 210],
    "1100": [1025, 300],   "1101": [975, 390],    "1110": [525, 390],    "1111": [475, 300],    "1120": [1025, 480],   "1121": [475, 480],
}       # A dictionary to store the positions of the images and the probabilities, vector and polar labels of each state (added later)

basis_states = state_dict.keys()

# GUI window
window = tk.Tk()

# File handling
BASE_DIR = Path(__file__).resolve().parent

# Parameters
scale_v = tk.DoubleVar(window, 1/8) # Initial variable for the scale (used for the step magnitude)
helv28 = tkFont.Font(family='Helvetica', size=28, weight=tkFont.BOLD)
helv26 = tkFont.Font(family='Helvetica', size=26, weight=tkFont.BOLD)
helv20 = tkFont.Font(family='Helvetica', size=20, weight=tkFont.BOLD)
helv14 = tkFont.Font(family='Helvetica', size=14)
math12 = ("Cambria Math",12,"bold")
magenta_hex = "#FF00FF"
orange_hex = "#FFC20B"
cyan_hex = "#00FFFF"
black = "#000000"
white = "#FFFFFF"
colour_chose = {"Dark":white, "Light":black} # Colour themes

# Toggle buttons (magnitude and angle) variables
v = tk.StringVar(window, "1")
is_on_angle = False
is_on_mag = True
toggle_vis = True

# Initialise these variables to be not on or default
step_counter = 0
end_game = "N"
key_option = tk.StringVar(window,"Classic")
col_option = tk.StringVar(window,"Dark")
options_class = tk.IntVar(window,1)
options_quant = tk.IntVar(window,2)
options_rep = tk.IntVar(window,3)
options_count = tk.IntVar(window,4)
options_prop = tk.IntVar(window,5)

# Karina is lazy
pi = np.pi

op_sys = os.name # What operating system are you
if op_sys == 'posix': # Apple
    tk_lib = ttk # ttk library works better

    style = ttk.Style(window)
    try:
        style.theme_use('clam')
    except Exception:
        pass  # fall back silently if 'clam' isn't available

    # CMY styles to match graph edges
    style.configure('Magenta.TButton', background=magenta_hex, foreground='black', font=helv26, padding=4)
    style.configure('Yellow.TButton',  background=orange_hex, foreground='black', font=helv26, padding=4)
    style.configure('Cyan.TButton',    background=cyan_hex, foreground='black', font=helv26, padding=4)

    # Hover/pressed states
    style.map('Magenta.TButton', background=[('active', magenta_hex)])
    style.map('Yellow.TButton',  background=[('active', orange_hex)])
    style.map('Cyan.TButton',    background=[('active', cyan_hex)])

    magenta = 'Magenta.TButton'
    orange = 'Yellow.TButton'
    cyan = 'Cyan.TButton'

    style_op = lambda colour_button: {"style": colour_button} # Choose what kind of style button 
    space="" # No space needed 

else: #op_sys == 'nt' # Everyone else
    tk_lib = tk  #tk library works better

    magenta = magenta_hex
    orange = orange_hex
    cyan = cyan_hex

    style_op = lambda colour_hex: {"font": helv26, "bd": 0, "bg": colour_hex} # Choose what kind of font colour
    space="  " # Space needed


# Matrices and logs
R2_matrix, U2_matrix, F2_matrix = pm.perm_matrix()
P24 = np.identity(24)
P24[0, 0] = -1

HamR2 = 1j * spla.logm(R2_matrix)
HamU2 = 1j * spla.logm(U2_matrix) #(pi/2 + pi ) * (R2_matrix-np.identity(24))
HamF2 = 1j * spla.logm(F2_matrix) 
Hamb = 1j * spla.logm(R2_matrix@U2_matrix) #(2*pi*np.sqrt(3)/9 + 2*pi/np.sqrt(3) )*(R2_matrix@U2_matrix-np.linalg.inv(R2_matrix@U2_matrix)) * 1j
HambInv = 1j * spla.logm(U2_matrix@R2_matrix)
Hamh = 1j * spla.logm(R2_matrix@U2_matrix@R2_matrix) 
Ham2 = 1j * spla.logm(R2_matrix@U2_matrix@R2_matrix@F2_matrix ) # Example 1  (2-cycle)   
Ham3 = 1j * spla.logm(R2_matrix@U2_matrix@F2_matrix@R2_matrix) # Example 2 (3-cycle)
Ham4 = 1j * spla.logm(R2_matrix@U2_matrix@F2_matrix) # Example 3 (4-cycle)
Ex5 = (pi/4) *((-R2_matrix@U2_matrix@F2_matrix + np.identity(24) - np.linalg.inv(R2_matrix@U2_matrix@F2_matrix) + R2_matrix@U2_matrix@F2_matrix@R2_matrix@U2_matrix@F2_matrix) + 1j * (R2_matrix@U2_matrix@F2_matrix-np.linalg.inv(R2_matrix@U2_matrix@F2_matrix)))
Ex6 = (pi/4) *((-R2_matrix@U2_matrix@F2_matrix + 3*np.identity(24) - np.linalg.inv(R2_matrix@U2_matrix@F2_matrix) - R2_matrix@U2_matrix@F2_matrix@R2_matrix@U2_matrix@F2_matrix) + 1j * (R2_matrix@U2_matrix@F2_matrix-np.linalg.inv(R2_matrix@U2_matrix@F2_matrix)))
Ex7 = (pi/4) *((R2_matrix@U2_matrix@F2_matrix - 3*np.identity(24) + np.linalg.inv(R2_matrix@U2_matrix@F2_matrix) + R2_matrix@U2_matrix@F2_matrix@R2_matrix@U2_matrix@F2_matrix) + 1j * (R2_matrix@U2_matrix@F2_matrix-np.linalg.inv(R2_matrix@U2_matrix@F2_matrix)))
Ex8 = pi/3 *(2*np.identity(24)-R2_matrix@U2_matrix-R2_matrix@U2_matrix@R2_matrix@U2_matrix-1j*(1/np.sqrt(3))*(R2_matrix@U2_matrix-R2_matrix@U2_matrix@R2_matrix@U2_matrix))
Ex9 = pi/3 *(-2*np.identity(24)+R2_matrix@U2_matrix+R2_matrix@U2_matrix@R2_matrix@U2_matrix-1j*(1/np.sqrt(3))*(R2_matrix@U2_matrix-R2_matrix@U2_matrix@R2_matrix@U2_matrix))
HamP = 1j * spla.logm(P24)

# Create quantum circuit (starts with 0000)
def create_new_circuit():
    circuit = QuantumCircuit()
    qube = QuantumRegister("qube", 4, [2,2,3,2])
    circuit.append(qube)

    return circuit, qube

circuit, qube = create_new_circuit()
provider = MQTQuditProvider()
backend = provider.get_backend("tnsim")

# This general circuit runs any move depending on the time step (default 1/8 for quantum and 1 for classical), the Hamiltonian, and the qubits (always the same)
# Returns the state: quantum state in the computational basis (24x1 array) and probabilities (24x1 array). 
def general_circuit(time_step, Ham):

    U = spla.expm(-1j*time_step*Ham)

    circuit.cu_multi([qube[0],qube[1],qube[2],qube[3]], U)

    state = circuit.simulate()
    probs = np.abs(state)**2

    return state[0], probs[0]

def reset_circuit(): # A circuit that only has StatePrep for resetting. StatePrep: Prepare subsystems using a state vector in the computational basis
    global circuit, qube
    circuit,qube = create_new_circuit()

    state = circuit.simulate()
    probs = np.abs(state)**2

    return state[0], probs[0] # state and probs returns e.g. [0,0,0,0,0.707,0.707,0,0,...,0] and [0,0,0,0,0,0.5,0.5,0,0,...,0].

def measure_cube():
    global circuit, qube
    job = backend.run(circuit)
    result = job.result()

    state = result.get_state_vector()
    measurement = measure_state(state) # Gives integer of result, e.g. 0=0000, 1=0001, 2=0010, ..., 23=1121

    state = [0] * measurement + [1 + 0j] + [0] * (23-measurement) #e.g. [0] * 1 + [1] + [0] * 22 = [0,1,0,0,0,0,0,0,0,0,...,0] (integer tells us where the 1 is)
    probs = np.abs(state)**2

    circuit,qube = create_new_circuit()
    prep = StatePrep(circuit, state, approx=False)
    circuit = prep.compile_state()

    return state, probs 

# The main function - this is run every time a button is pressed 
# runs the move -> gets final state and probabilities -> under each bit value stores the vector (from state), probabilities, and polar (converts from state)
# -> calculates transparency (255 if magnitude is off) and places circles representing polar angle (if angle is on) -> place background Nauru graph
# -> place cube images with certain transparency -> place labels under cubes -> end game (if conditions meet)
def main(Ham=None, time_step=1):
    global current_image, state_dict, image_refs, background_image, step_counter, end_game # yes I know so many globals

    # Skips if just want to run image update not run another move 

    if type(Ham) != NoneType: 
        try: # For classical and quantum moves
            result, probs = general_circuit(time_step, Ham)
            step_counter += abs(time_step) # Absolute because you can have negative time steps

        except: # For measure and reset circuits
            try:
                result, probs = Ham()

            except Exception as e: # When that stupid bug pops up :(
                print(e)
                messagebox.showwarning(title="Whoops", message="Oh no you've found the bug Karina can't get rid of.\nShe'll get some bug spray soon. Sit tight.\nIn the meantime you can't measure this state sorry.")
                return # Breaks out of function early (or else it will keep giving errors which is annoying -> this bug prevents measurement)

        label_list[1].config(text="Number of moves: "+str(sf.round(step_counter, decimals=2))) # Update number of steps

        for basis_state,state,prob in zip(basis_states,result,probs): 

            state_pol = cmath.polar(state)

            state_dict[basis_state][2] = state_pol # Store polar values in dictionary (r,theta)
            state_dict[basis_state][3] = prob # Store probabilities in dictionary
            state_dict[basis_state][4] = state # Store vector values in dictionary

    # Delete previous images 
    image_refs = []
    canvas.delete("current_image")
    canvas.delete("circle")
    canvas.delete("Nauru_graph")
    canvas.delete("initial_text")
    canvas.delete("congrats")

    # Insert/update angle circles (if on) and/or calculate transparency depending on magnitude (this uses the polar form)
    for basis_state in basis_states:

        if state_dict[basis_state][3] >= 1e-3: # Percentage has to be greater than 0.1% (0.001 in dictionary) -> aligns with label now
            if is_on_mag == True:
                transparency = int(255 * state_dict[basis_state][2][0]) # polar (radius) ∈ [0,1] ----> polar (radius) x 255 ∈ [0,255] (this works with colour/transparency)
            else:
                transparency = 255 # Leave full transparency 

            if is_on_angle == True:
                hue = (state_dict[basis_state][2][1] / (2*np.pi)) % 1.0 # polar (angle) ∈ (-pi,pi] ----> ∈ (-0.5,0.5] ----> hue ∈ [0,1] 
                
                if col_option.get()== "Dark": lum = 0.5/255*transparency # Make circles as transparent as cubes
                else: lum = 1-0.5/255*transparency

                if lum > 0.025: # If too dark it's just a black circle which looks terrible
                    canvas.create_oval(state_dict[basis_state][0]-50, state_dict[basis_state][1]-50,state_dict[basis_state][0]+50, 
                                    state_dict[basis_state][1]+50, fill=colour.Color(hue=hue, saturation=1, luminance = lum),outline="", tags="circle")

    image_path = BASE_DIR/"images"/"honeycomb_connections_cmy.png" # os.path.join depends on the operating system
    background_image = tk.PhotoImage(file=image_path)
    canvas.create_image(750, 400, image=background_image, tags = "Nauru_graph") # Nauru graph

    # Place cube images in locations
    
    for basis_state in basis_states:
        if state_dict[basis_state][3] >= 1e-3: # Percentage has to be greater than 0.1% (0.001 in dictionary) -> aligns with label now

            im = Image.open(BASE_DIR/"images"/f"{basis_state}.png")
            im_resize = im.resize((im.width // 5, im.height // 5)) # This reduces the size without losing quality yay
            alpha_pixels = list(im_resize.getdata()) # Pixels

            if is_on_mag == True:
                transparency = int(255 * state_dict[basis_state][2][0]) # polar (magnitude) ∈ [0,1] ----> polar (radius) x 255 ∈ [0,255] (this works with colour/transparency)
            else:
                transparency = 255 # Leave full transparency 
            
            for index,pixel in enumerate(alpha_pixels):
                if pixel[3] != 0: # Leave already transparent pixels transparent - pixel[3] = transparent/alpha pixels
                    temp = list(alpha_pixels[index]) # Make list of RGBalpha
                    temp[3] = transparency # Make transparency value the alpha value in list 
                    alpha_pixels[index] = tuple(temp) # Put new pixel back in
                    
            im_resize.putdata(alpha_pixels) # Update pixels
            img = ImageTk.PhotoImage(im_resize)
            canvas.create_image(state_dict[basis_state][0],state_dict[basis_state][1],image=img) # Put image in!
            image_refs.append(img) # Solution to trash collecting bug (keep images as a variable or else it will forget it)

    # Place labelling on each cube
    rep_change()

    # End game sequence
    if result[0] == 1+0j and end_game=="Y":
        canvas.create_text(700, 400,text="CONGRATULATIONS", font=helv28, fill=colour_chose[col_option.get()], tags="congrats")
        canvas.delete("Nauru_graph")

        # Disable all buttons except reset button
        for button in button_list+radbuttons:
            button.config(state=tk.DISABLED)

        if toggle_vis == True:
            canvas.itemconfigure(toggle_button_angle, state = tk.DISABLED)
            canvas.itemconfigure(toggle_button_mag, state = tk.DISABLED)

        # Only when user presses return does the keys regain their functions
        def reset(event):
            window.bind('<Key>', on_key_press)
            reset_cube()

        window.unbind('<Key>', window.bind('<Key>', on_key_press))
        window.bind('<Return>', reset)
        
# What happens when you press specific keys on your keyboard
def on_key_press(event):
    time_step = scale_v.get()
    key = key_option.get()

    if key == 'Classic': # This is the default. Press keys r,u and f.
        keyboard = {'R2':'r','U2':'u','F2':'f'} 
    elif key == "Efficient": # Alternative. Press keys right, up and left.
        keyboard = {'R2':'right','U2':'up','F2':'left'}

    if event.keysym.lower()==keyboard['R2']:
        if event.state == 262148 or event.state == 4: # ctrl r
            main(HamR2)
        elif event.state == 262144 or event.state == 0: # r
            main(HamR2,time_step=time_step)
        elif event.state == 262145 or event.state == 1: # shift r
            main(HamR2,time_step=-time_step)
        
    elif event.keysym.lower()==keyboard['U2']:
        if event.state == 262148 or event.state == 4: # ctrl u
            main(HamU2)
        elif event.state == 262144 or event.state == 0: # u
            main(HamU2,time_step=time_step)
        elif event.state == 262145 or event.state == 1: # shift u
            main(HamU2,time_step=-time_step)

    elif event.keysym.lower()==keyboard['F2']:
        if event.state == 262148 or event.state == 4: # ctrl f
            main(HamF2)
        elif event.state == 262144 or event.state == 0: # f
            main(HamF2,time_step=time_step)       
        elif event.state == 262145 or event.state == 1: # shift f
            main(HamF2,time_step=-time_step)

    elif event.keysym=='b':
        main(Hamb,time_step=time_step)
    elif event.keysym=='B':
        main(Hamb,time_step=-time_step)

    elif event.keysym=='v' and event.state == 0:
        main(HambInv,time_step=time_step)
    elif event.keysym=='V':
        main(HambInv,time_step=-time_step)

    elif event.keysym=='h' and event.state == 0:
        main(Hamh,time_step=time_step)
    elif event.keysym=='H':
        main(Hamh,time_step=-time_step)

    elif event.keysym=='p' and event.state == 0:
        main(HamP,time_step=time_step)
    elif event.keysym=='P':
        main(HamP,time_step=-time_step)

    #### Extra moves (2-, 3-, and 4-cycle)
    elif event.keysym=='2':
        main(Ham2,time_step=time_step)
    elif event.keysym=='3':
        main(Ham3,time_step=time_step)
    elif event.keysym=='4':
        main(Ham4,time_step=time_step)

    #### Extra extra moves
    elif event.keysym=='at':
        main(Ham2,time_step=-time_step)
    elif event.keysym=='dollar':
        main(Ham4,time_step=-time_step)
    elif event.keysym=='5':
        main(Ex5,time_step=time_step)
    elif event.keysym=='percent':
        main(Ex5,time_step=-time_step)
    elif event.keysym=='6':
        main(Ex6,time_step=time_step)
    elif event.keysym=='asciicircum':
        main(Ex6,time_step=-time_step)
    elif event.keysym=='7':
        main(Ex7,time_step=time_step)
    elif event.keysym=='ampersand':
        main(Ex7,time_step=-time_step)
    elif event.keysym=='8':
        main(Ex8,time_step=time_step)
    elif event.keysym=='asterisk':
        main(Ex8,time_step=-time_step)
    elif event.keysym=='9':
        main(Ex9,time_step=time_step)
    elif event.keysym=='parenleft':
        main(Ex9,time_step=-time_step)

    elif event.keysym=='Return':
        reset_cube()
    elif event.keysym=='space':
        main(measure_cube)

# Function to reset the game to 100% solved state (0000)
def reset_cube():
    global step_counter, end_game

    step_counter = 0

    if end_game == "Y":
        window.bind('<Key>', on_key_press) # This is here if you win the game (to unlock the key functions)

        # Again only when you win the game (to unlock the frozen buttons)
        for button in button_list+radbuttons:
            button.config(state=tk.NORMAL)
        
        if toggle_vis == True:
            canvas.itemconfigure(toggle_button_angle, state = tk.NORMAL)
            canvas.itemconfigure(toggle_button_mag, state = tk.NORMAL)

        end_game = "N"

    main(reset_circuit) # To update the images and labels

# To label each cube either the percentage, vector or polar representation.
def rep_change():
    canvas.delete("text") 
    canvas.delete("initial_text")
    var = v.get() # var is the representation type chosen from the radiobuttons
    fill_colour = colour_chose[col_option.get()] # What font colour is the labels?

    for basis_state in basis_states:
        if state_dict[basis_state][2][0] != 0 or state_dict[basis_state][2][1] != 0:
            if var == "1": # Percentage
                label = sf.round(state_dict[basis_state][3]*100,sigfigs=3)
                if 0.1 > label >= 0.001: label = "< 0.1" # Only show percentages >0.001% and between 0.001 and 0.1 just label it <0.1%
                elif label == 100: label = 100 # Show 100.0% as 100%

                if label == "< 0.1" or label > 0.1:
                    canvas.create_text(state_dict[basis_state][0],(state_dict[basis_state][1]+60),
                                        text=str(label)+"%", 
                                        fill=fill_colour, font=math12, tags="text") # Create label (python labels this text)
                
            elif var == "2": # Vector
                label_vec = np.real_if_close((state_dict[basis_state][4])) # Eliminates super small imaginary values
                if abs(label_vec.real) >= 0.01 or abs(label_vec.imag) >= 0.01: # Only show if either the real or imaginary values are greater than 0.01
                    text = "{:.2f}".format(label_vec) # Round to 2 decimal points
                    if abs(label_vec.real) < 0.01:
                        text = "{:.2f}".format(label_vec.imag) + "i" # If just imaginary get rid of 0.00 + imag -> imag
                    canvas.create_text(state_dict[basis_state][0],(state_dict[basis_state][1]+60),
                                        text=(text.replace("(", "").replace(")", "").replace("j", "i")), 
                                        fill=fill_colour, font=math12, tags="text") # Create label (python labels this text)
                
            elif var == "3": # Polar
                label1 = "%.2f" % state_dict[basis_state][2][0] # Radius e.g. 0.3444 -> "0.34"
                label2 = Fraction(np.round(state_dict[basis_state][2][1]/pi,15)).limit_denominator() # Convert Angle to fraction and limit the denominator if the time step stuffs up
                if abs(state_dict[basis_state][2][0]) >= 0.01:
                    canvas.create_text(state_dict[basis_state][0],(state_dict[basis_state][1]+60),
                                        text=(f"{label1}exp(πi({label2}))"), #(label1+"exp("+str(label2)+" πi)")
                                        fill=fill_colour, font=math12, tags="text") # Create label (python labels this text)

# Function to be called if press angle toggle button
def toggle_angle(event):
    global is_on_angle

    if is_on_angle: # When toggling the angle button off 
        # Just delete all the circles
        canvas.delete("circle")
        canvas.delete("colour_wheel")
        canvas.delete("wheel_label1")
        canvas.delete("wheel_label2")
        canvas.delete("wheel_label3")
        canvas.delete("wheel_label4")
        canvas.itemconfigure(toggle_button_angle, image = canvas.off_image) # item_list = [e for e in item_list if e not in ('item', 5)]
        is_on_angle = False
    
    else: # When toggling the angle button on
        canvas.itemconfigure(toggle_button_angle, image = canvas.on_image)

        # Make the rainbow phase circle
        arc_width = 5 # This is as low as it goes - trust me i've tried
        num_arcs = int(360/arc_width)
        for arc in np.linspace(0,360,num_arcs,endpoint=False): #arc = 0,5,10,15,20,... 
            canvas.create_arc(1100,70,1200,170, fill=colour.Color(hue=arc_width*(arc)/360, saturation=1, luminance = 0.5), 
                            outline=colour.Color(hue=arc_width*(arc)/360, saturation=1, luminance = 0.5), start = arc_width*(arc), extent = arc_width, tags="colour_wheel") # The colour wheel made up of many many arcs

        # Colour of text depends on option of background
        colour_chose = {"Dark":white, "Light":black}

        # Colour wheel labelling 
        canvas.create_text(1215,120, text=0, font=("Cambria Math",12,"bold"), fill=colour_chose[col_option.get()], tags="wheel_label1")
        canvas.create_text(1085,120, text="π", font=("Cambria Math",12,"bold"), fill=colour_chose[col_option.get()], tags="wheel_label2")
        canvas.create_text(1150,55, text="π/2", font=("Cambria Math",12,"bold"), fill=colour_chose[col_option.get()], tags="wheel_label3")
        canvas.create_text(1150,185, text="-π/2", font=("Cambria Math",12,"bold"), fill=colour_chose[col_option.get()], tags="wheel_label4")

        is_on_angle = True # Update: angle toggle is on

        main() # Go through main function to add the phase circles

# Function to be called if press magnitude toggle button
def toggle_mag(event):
    global is_on_mag
    
    if is_on_mag: # When toggling the magnitude button off
        canvas.itemconfigure(toggle_button_mag, image = canvas.off_image)
        is_on_mag = False
    
    else: # When toggling the magnitude button on
        canvas.itemconfigure(toggle_button_mag, image = canvas.on_image)
        is_on_mag = True

    main() # Always go through main function whenever toggle magnitude button

# Function to scramble the board with random quantum moves depending on the time step
def QuScramble():
    global step_counter, end_game

    time_step = scale_v.get()

    choice = {"R2":HamR2, "U2":HamU2, "F2":HamF2} # There are three choice for the three moves

    for _ in range(100):
        QuMove = np.random.choice(["R2", "U2", "F2"]) # Choose any of the three moves (this is a string cause it doesn't work with matrices)
        result = general_circuit(time_step, choice[QuMove])[0] # Access only the result with [0] (else you have to do result,probs = )
    
    end_game = "Y" # end_game is global as many functions will be called before the game will end
    step_counter -= time_step
    main(HamR2,time_step=time_step) # Do it one more time with quantum R2

# Function to set the scrolling on button as the quantum move or inverse quantum move depending on the direction of scrolling. Only when the mouse is over the button. 
def set_mousewheel(widget):
    widget.bind("<Enter>", lambda _: widget.bind_all('<MouseWheel>', scroll))
    widget.bind("<Leave>", lambda _: widget.unbind_all('<MouseWheel>'))

def scroll(event):
    time_step = scale_v.get()
    if event.delta == -120: # Forward scroll
        main(event.widget.command,time_step=time_step)
    elif event.delta == 120: # Backward scroll
        main(event.widget.command,time_step=-time_step)

# Help -> Keyboard Shortcuts
def pop_up():
    option = key_option.get()
    if option == 'Classic': # This is the default. Press keys r,u and f.
        image = "keyboard_shortcuts.png"
    elif option == "Efficient": # Alternative. Press keys right, up and left.
        image = "keyboard_shortcuts_alt.png"

    popup_path = Image.open(BASE_DIR/"images"/image)
    popup_path.thumbnail((960,540)) # Similar to .resize()
    popup_image = ImageTk.PhotoImage(popup_path)

    Help = tk.Label(window, image=popup_image)
    Help.image = popup_image
    Help.place(x=170,y=100)

    def destroy(event):
        Help.destroy()
        window.unbind('<KeyPress>') # No keys do anything
        window.bind('<Key>', on_key_press) # Keys do their specific function     

    window.bind('<KeyPress>', destroy) # If press key then destroy the big white square and rebind the key functions.

def preferences(pref_type):
    child_window = tk.Toplevel(window)  # Create a new window
    child_window.geometry("300x100") # Make it a small window of size 300x100
    child_window.resizable(False,False) # Stays the size no matter what

    if pref_type == "options": # If clicked the Key Options tab
        child_window.title("Adjust key settings") # Title of the little window

        pref_combo = ttk.Combobox(child_window, state="readonly",
                                    values=["Classic","Efficient"],
                                    textvariable=key_option) # Key settings of either classic or efficient (ruf keys or arrow keys)
        pref_combo.set(key_option.get()) # Set the default selected option as the current selection

    elif pref_type == "colour_change": # If clicked the Colour Options tab
        child_window.title("Adjust colours") # Title of the little window
        
        pref_combo = ttk.Combobox(child_window, state="readonly",
                                    values=["Dark", "Light"],
                                    textvariable=col_option) # Colour settings of either dark or light (background)
        
        def colour_change(event): # Inverts the colours from black-> white or white->black
            
            # Check what theme is selected and update the colours of the text to the opposite colour 
            if col_option.get() == "Dark": # Check what is selected
                colour_chose = [black,white] # Make black the background
            elif col_option.get() == "Light": # Check what is selected
                colour_chose = [white,black] # Make white the background

            canvas.configure(bg=colour_chose[0]) # Change colour of background of window
            button_list[9].config(bg=colour_chose[1],fg=colour_chose[0]) # Change background colour of measure button
            for i in range(len(label_list)): # 0,1,2,3,4...
                try:
                    label_list[i].config(foreground=colour_chose[1], background=colour_chose[0]) # change colour of labels and scale
                except:
                    canvas.itemconfig(label_list[i],fill=colour_chose[1]) # change colour of canvas.create_text()

            main() # Update the colour of the state labels and phase circles
            
        pref_combo.bind("<<ComboboxSelected>>", colour_change) # Binds the function to when you select an option in the combobox
        
    # Exit button - deletes the small window
    exit_button = tk.Button(child_window, 
            text='OK', 
            cursor="hand2",
            width=5,
            bd=0,
            bg='light grey',
            activebackground='light blue',
            command=lambda:child_window.destroy())

    pref_combo.pack(side=tk.TOP, pady=20) # Use pack because it stacks the widgets nicely but need some padding (pady)
    exit_button.pack(side=tk.BOTTOM, pady=10)

def display_options(change_display):
    global toggle_vis

    if change_display == 1:
        button_list[0].place(x=50, y=250)
        button_list[1].place(x=50, y=350)
        button_list[2].place(x=50, y=450)
    elif change_display == 10:
        for i in range(3):
            button_list[i].place_forget()
    
    elif change_display == 2:
        button_list[3].place(x=268, y=250)
        button_list[6].place(x=200, y=250)
        button_list[4].place(x=268, y=350)
        button_list[7].place(x=200, y=350)
        button_list[5].place(x=268, y=450)
        button_list[8].place(x=200, y=450)
        button_list[9].place(x=105, y=550)
        button_list[10].place(x=400, y=675)
        label_list[4].place(x=215, y=180)
        canvas.itemconfigure(clock,state='normal')
        canvas.itemconfigure(anti_clock,state='normal')
    elif change_display ==  20:
        for i in range(3,11):
            button_list[i].place_forget()
        label_list[4].place_forget()
        canvas.itemconfigure(clock,state='hidden')
        canvas.itemconfigure(anti_clock,state='hidden')

    elif change_display == 3:
        difference=0
        for i in range(4):
            radbuttons[i].place(x=1150, y=(250+difference))
            difference += 100
    elif change_display == 30:
        for i in range(4):
            radbuttons[i].place_forget()

    elif change_display == 4:
        label_list[1].place(x=50, y=70)
    elif change_display == 40:
        label_list[1].place_forget()

    elif change_display == 5:
        canvas.itemconfigure(toggle_button_angle, state='normal')
        canvas.itemconfigure(toggle_button_mag, state='normal')
        canvas.itemconfigure(label_list[2], state='normal')
        canvas.itemconfigure(label_list[3], state='normal')
        toggle_vis = True
    elif change_display == 50:
        canvas.itemconfigure(toggle_button_angle, state='hidden')
        canvas.itemconfigure(toggle_button_mag, state='hidden')
        canvas.itemconfigure(label_list[2], state='hidden')
        canvas.itemconfigure(label_list[3], state='hidden')
        toggle_vis = False
        
    

# This is the GUI function and is the first to be called
def GUI():
    global current_image, canvas, toggle_button_angle, toggle_button_mag,label_list, radbuttons, button_list, clock, anti_clock


    ###########  Initialisation  ##############

    initial_state = [1 + 0j] + [0] * 23 # This starts the cube in the solved state

    # Add three extra items in the cube dictionary for the polar,percentage,vector. One dictionary item is now [posx,posy,(radius,angle),percentage,vector]
    for basis_state,state in zip(basis_states,initial_state):

        state_pol = cmath.polar(state)

        state_dict[basis_state].append(state_pol) # Polar
        state_dict[basis_state].append(np.real(state)) # Percentage
        state_dict[basis_state].append(state) # Vector

    ###########################################

    window.geometry("1300x800") # Size of GUI window
    window.minsize(1300,800)
    window.maxsize(1300,800)
    window.title('Move the QUBE') # Title of GUI window

    frame = tk.Frame(window) # Frame inside window - needed for canvas
    frame.place(x=0,y=0)

    canvas = tk.Canvas(frame, bg="#000000", width=1300, height=800) # Created a canvas (needed for creating images, text, circles, etc.)
    canvas.pack()

    # Create a menu bar with File and Help. File has a sub menu with Preferences and Exit. Preferences has a sub menu Options and Accessibility. Help has a sub menu with just Keyboard Shortcuts.
    # File              Help
    # -> Preferences    -> Keyboard Shortcuts
    #    -> Key Options
    #    -> Colour Options     
    # -> Display
    #    -> Buttons
    #        -> Classical
    #            -> R2  -> U2  -> F2
    #        -> Quantum
    #            -> QuR2  -> QuU2  -> QuF2
    #        -> Other
    #            -> Scramble  -> Reset  -> Measure
    #    -> Label
    # -> Exit           
    menubar = tk.Menu(window) 
    window.config(menu=menubar)
    file_menu = tk.Menu(menubar, tearoff=False)
    help_menu = tk.Menu(menubar,tearoff=False)

    sub_menu = tk.Menu(file_menu, tearoff=False)
    sub_menu.add_command(label='Key Options', command=lambda: preferences("options")) # Use lambda to specify a parameter in a function
    sub_menu.add_command(label='Colour Options', command=lambda: preferences("colour_change"))

    display_menu = tk.Menu(file_menu, tearoff=False)
    display_menu.add_checkbutton(label="Classical", onvalue=1, offvalue=10, variable=options_class, command=lambda:display_options(options_class.get()))
    display_menu.add_checkbutton(label="Quantum", onvalue=2, offvalue=20, variable=options_quant, command=lambda:display_options(options_quant.get()))
    display_menu.add_checkbutton(label="Representations", onvalue=3, offvalue=30, variable=options_rep, command=lambda:display_options(options_rep.get()))
    display_menu.add_checkbutton(label="Move Counter", onvalue=4, offvalue=40, variable=options_count, command=lambda:display_options(options_count.get()))
    display_menu.add_checkbutton(label="State Properties", onvalue=5, offvalue=50, variable=options_prop, command=lambda:display_options(options_prop.get()))

    file_menu.add_cascade(label="Preferences", menu=sub_menu)
    file_menu.add_cascade(label="Display", menu=display_menu)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=window.destroy)
    menubar.add_cascade(label="File", menu=file_menu)

    help_menu.add_command(label="Keyboard Shortcuts",command=pop_up)
    menubar.add_cascade(label="Help", menu=help_menu)

    label1 = tk.Label(
        text="The Rubik's Qube Game", # This is the heading
        font=helv28,
        foreground="white",  # Set the text color to white
        background="black"  # Set the background color to black
    )

    label2 = tk.Label(
        text = "Number of moves: "+str(step_counter), # Step counter in the top left
        font = helv14,
        foreground = "white",
        background = "black"
    )

    # Nauru graph image
    image_path = BASE_DIR/"images"/"honeycomb_connections_cmy.png"
    
    background_image = tk.PhotoImage(file=image_path)
    canvas.create_image(750, 400, image=background_image, tags="Nauru_graph")

    # Solved state cube image
    im = Image.open(BASE_DIR/"images"/"0000.png")
    im_resize = im.resize((im.width // 5, im.height // 5))
    current_image = ImageTk.PhotoImage(im_resize)
    canvas.create_image(state_dict["0000"][0],state_dict["0000"][1],image=current_image, tags="current_image")
    
    # Cube label
    canvas.create_text(state_dict["0000"][0],(state_dict["0000"][1]+60), text="100%", fill="white", font=("Cambria Math",12,"bold"), tags="initial_text")

    # Rainbow image for quantum scramble button
    rainbow = Image.open(BASE_DIR/"images"/"rainbow.png")
    rainbow_resize = rainbow.resize((150,60))
    rainbow = ImageTk.PhotoImage(rainbow_resize)

    # Clockwise and anticlockwise image to go on top of QuR2 buttons to indicate move and inverse move
    anti_clock = Image.open(BASE_DIR/"images"/"anti_clock.png")
    anti_clock_resize = anti_clock.resize((anti_clock.width//10, anti_clock.height//10))
    canvas.anti_clock = ImageTk.PhotoImage(anti_clock_resize)
    clock = Image.open(BASE_DIR/"images"/"clock.png")
    clock_resize = clock.resize((40,40))
    canvas.clock = ImageTk.PhotoImage(clock_resize)

    anti_clock = canvas.create_image(330,250,image=canvas.anti_clock)
    clock = canvas.create_image(200,250,image=canvas.clock)

    # On and Off button for the magnitude and angle buttons
    on = Image.open(BASE_DIR/"images"/"toggle_on.png")
    off = Image.open(BASE_DIR/"images"/"toggle_off.png")
    canvas.on_image = ImageTk.PhotoImage(on.resize((on.width // 16, on.height // 16)))
    canvas.off_image = ImageTk.PhotoImage(off.resize((on.width // 16, on.height // 16)))
    toggle_button_angle = canvas.create_image(1210, 650, image = canvas.off_image)
    toggle_button_mag = canvas.create_image(1210, 700, image = canvas.on_image)

    # All the buttons with various properties. tk_lib is tk for windows and ttk for mac.
    R2_button = tk_lib.Button(window, 
                    text='R2', 
                    width=5, 
                    cursor="hand2",
                    **style_op(magenta),
                    command=lambda: main(HamR2))

    U2_button = tk_lib.Button(window, 
                    text='U2', 
                    width=5,
                    cursor="hand2",
                    **style_op(orange),
                    command=lambda: main(HamU2))

    F2_button = tk_lib.Button(window, 
                    text='F2', 
                    width=5, 
                    cursor="hand2",
                    **style_op(cyan),
                    command=lambda: main(HamF2))
    
    Qu_R2_button = tk_lib.Button(window, 
                    text='R2'+space, 
                    width=3, #6
                    cursor="hand2", 
                    **style_op(magenta),
                    command=lambda: main(HamR2,time_step=scale_v.get())) 
    
    Inv_Qu_R2_button = tk_lib.Button(window, 
                    text=space+'Qu', 
                    width=3,
                    cursor="hand2",
                    **style_op(magenta),
                    command=lambda: main(HamR2,time_step=-scale_v.get())) 
    
    Qu_U2_button = tk_lib.Button(window, 
                    text='U2'+space,
                    width=3,
                    cursor="hand2", 
                    **style_op(orange), 
                    command=lambda: main(HamU2,time_step=scale_v.get()))
    
    Inv_Qu_U2_button = tk_lib.Button(window, 
                    text=space+'Qu',
                    width=3,
                    cursor="hand2", 
                    **style_op(orange),
                    command=lambda: main(HamU2,time_step=-scale_v.get()))

    Qu_F2_button = tk_lib.Button(window, 
                    text='F2'+space,
                    width=3,
                    cursor="hand2", 
                    **style_op(cyan),
                    command=lambda: main(HamF2,time_step=scale_v.get()))  
    
    Inv_Qu_F2_button = tk_lib.Button(window, 
                    text=space+'Qu',
                    width=3,
                    cursor="hand2", 
                    **style_op(cyan),
                    command=lambda: main(HamF2,time_step=-scale_v.get()))
    
    reset_button = tk.Button(window, 
                    text='Reset',
                    font = helv20,
                    width=5, 
                    bd = 0,
                    bg = "grey",
                    cursor="hand2",
                    command=lambda: reset_cube())
    
    measure_button = tk.Button(window, 
                    text='Measure',
                    font = helv28,
                    width=7, 
                    bd = 0,
                    bg = "white",
                    cursor="target",
                    command=lambda: main(measure_cube))
    
    Qu_scramble_button = tk.Button(window, 
                    image = rainbow,
                    font = helv20,
                    fg = "black",
                    bd = 0,
                    bg = "black",
                    text = "Scramble",
                    cursor="box_spiral",
                    compound="center",
                    command=lambda: QuScramble())
    
    values = {"Probability" : "1",
              "Vector" : "2",
              "Polar" : "3",
              "None" : "4"} # Representation radio button options with designated 1,2,3 and 4 (this is referred later)
    
    time_step_scale = tk.Scale(window, 
                    variable=scale_v, 
                    from_=1/128, to=1/2,      
                    orient="horizontal", 
                    resolution=1/128, digits=7,
                    bg = "black", fg="white",
                    highlightthickness=0) # Spits out decimals even though the resolution is fractions.

    
    canvas.tag_bind(toggle_button_angle,"<Button-1>", toggle_angle) # Bind the button to the function toggle_angle
    canvas.tag_bind(toggle_button_mag,"<Button-1>", toggle_mag) # Bind the button to the function toggle_magnitude. Uses tag_bind because these are actually images not buttons
    angle = canvas.create_text(1125,650, text="Phase", font=("Helvetica",12,"bold"), fill="white") # Angle text
    mag = canvas.create_text(1108,700, text="Amplitude", font=("Helvetica",12,"bold"), fill="white") # Magnitude text

    # Place all the buttons and scale with specified x and y locations.
    
    label1.place(x=430,y=10)
    label2.place(x=50, y=70)
    R2_button.place(x=50, y=250)
    U2_button.place(x=50, y=350)
    F2_button.place(x=50, y=450)
    Qu_R2_button.place(x=268, y=250)
    Inv_Qu_R2_button.place(x=200, y=250)
    Qu_U2_button.place(x=268, y=350)
    Inv_Qu_U2_button.place(x=200, y=350)
    Qu_F2_button.place(x=268, y=450)
    Inv_Qu_F2_button.place(x=200, y=450)
    reset_button.place(x=50, y=120)
    measure_button.place(x=105, y=550)
    Qu_scramble_button.place(x=400, y=675)
    time_step_scale.place(x=215, y=180)

    # This is done to allow for the scrolling
    Qu_R2_button.command = general_circuit
    Qu_U2_button.command = general_circuit
    Qu_F2_button.command = general_circuit
    Inv_Qu_R2_button.command = general_circuit
    Inv_Qu_U2_button.command = general_circuit
    Inv_Qu_F2_button.command = general_circuit
    set_mousewheel(widget=Qu_R2_button)
    set_mousewheel(widget=Qu_U2_button)
    set_mousewheel(widget=Qu_F2_button)
    set_mousewheel(widget=Inv_Qu_R2_button)
    set_mousewheel(widget=Inv_Qu_U2_button)
    set_mousewheel(widget=Inv_Qu_F2_button)
    

    difference = 0 # Set 0 for the for loop
    button_list = [R2_button, U2_button, F2_button, Qu_R2_button, Qu_U2_button, Qu_F2_button,
                   Inv_Qu_R2_button, Inv_Qu_U2_button, Inv_Qu_F2_button, measure_button, Qu_scramble_button] # Need a list for the for loop
    radbuttons = [] # To avoid trash collecting bug
    label_list = [label1,label2,angle,mag,time_step_scale,"wheel_label1","wheel_label2","wheel_label3","wheel_label4"]

    for (text, value) in values.items(): # Make four radiobuttons
        radbutton = tk.Radiobutton(window, text=text, variable=v, value=value,
                    indicator=0, background="grey", fg="black",
                    font = ("helvetica", 14, "bold"), width=9, cursor="hand2",
                    command=lambda: rep_change())
        radbutton.place(x=1150, y=(250+difference))
        radbuttons.append(radbutton) # To avoid trash collecting bug

        difference += 100

    window.bind('<Key>', on_key_press) # Bind the keyboard functions

    window.mainloop()

GUI()