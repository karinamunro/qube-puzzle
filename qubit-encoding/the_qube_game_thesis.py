######################################################################
# Note:
# Needs cube_images folder and perm_matrices.py

######################################################################

# Packages
import pennylane as qml
import numpy as np
import tkinter as tk
from tkinter import font as tkFont
from tkinter import messagebox
import perm_matrices as pm
import cmath
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import colour
import sigfig as sf
from fractions import Fraction
import scipy.linalg as spla
from types import NoneType
import os

IMAGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cube_images")

qubits = ['w','x','y1','y2','z'] # 5 qubits to represent 24 states: w_2 x_2 y1_2 y2_2 z_2
state_dict = {
    "00000": [690, 300],    "00001": [640, 390],    "00100": [860, 390],    "00101": [810, 300],    "00110": [690, 480],    "00111": [810, 480],
    "01000": [860, 570],    "01001": [810, 660],    "01100": [690, 120],    "01101": [975, 570],    "01110": [525, 210],    "01111": [640, 210],
    "10000": [525, 570],    "10001": [810, 120],    "10100": [690, 660],    "10101": [640, 570],    "10110": [860, 210],    "10111": [975, 210],
    "11000": [1025, 300],   "11001": [975, 390],    "11100": [525, 390],    "11101": [475, 300],    "11110": [1025, 480],   "11111": [475, 480],
}       # A dictionary to store the positions of the images and the probabilities, vector and polar labels of each state (added later)

# GUI window
window = tk.Tk()

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

# Initialise these variables to be not on or default
step_counter = 0
end_game = "N"
key_option = tk.StringVar(window,"Classic")
col_option = tk.StringVar(window,"Dark")
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
HamR2 = 1j * spla.logm(R2_matrix) # Quantum R2 move
HamU2 = 1j * spla.logm(U2_matrix) # Quantum U2 move
HamF2 = 1j * spla.logm(F2_matrix) # Quantum F2 move
Hamb = 1j * spla.logm(R2_matrix@U2_matrix) # Quantum b move
HambInv = 1j * spla.logm(U2_matrix@R2_matrix) # Quantum b^-1 move
Hamh = 1j * spla.logm(R2_matrix@U2_matrix@R2_matrix) # Quantum h move
Ham2 = 1j * spla.logm(R2_matrix@U2_matrix@R2_matrix@F2_matrix ) # Quantum rurf move (2-cycle)
Ham3 = 1j * spla.logm(R2_matrix@U2_matrix@F2_matrix@R2_matrix) # Quantum rufr move (3-cycle)
Ham4 = 1j * spla.logm(R2_matrix@U2_matrix@F2_matrix) # Quantum ruf move (4-cycle)

# Creates a custom pennylane gate from the input Hamiltonian.
class HamG(qml.operation.Operation):
    num_params = 2
    num_wires = 5
    par_domain = "L"

    @staticmethod
    def compute_matrix(*params):
        s = params[0]
        Ham = params[1]
        G = spla.expm(-1j*s*Ham)
        return G
    
# Pennylane quantum 'device'. There are many options in pennylane but 'default.qubit' is fine. qubits = ['w','x','y1','y2','z']
# 'default.qubit': a simple state simulator of qubit-based quantum circuit architectures - pennylane
dev = qml.device('default.qubit', wires=qubits)

# Uses a decorator: This decorator converts a Python function containing PennyLane quantum operations to a QNode circuit that will run on a quantum device - pennylane
# This general circuit runs any move depending on the time step (default 1/8 for quantum and 1 for classical), the Hamiltonian, and the qubits (always the same)
# Returns the state: quantum state in the computational basis (32x1 array) and probabilities (32x1 array). 
@qml.qnode(dev)
def general_circuit(Initial_State, time_step, Ham):
    qml.StatePrep(Initial_State, wires = qubits)
    HamG(time_step, Ham, wires = qubits)
    return qml.state(), qml.probs()

@qml.qnode(dev)
def reset_circuit(Initial_State): # A circuit that only has StatePrep for resetting. StatePrep: Prepare subsystems using a state vector in the computational basis
    qml.StatePrep(Initial_State, wires = qubits)
    return qml.state(), qml.probs() # state and probs returns e.g. [0,0,0,0,0.707,0.707,0,0,...,0] and [0,0,0,0,0,0.5,0.5,0,0,...,0].

dev = qml.device('default.qubit', wires=qubits, shots=1) #  Change device to include shots. This is required to do qml.sample(). qml.sample() is required to return qml.measure().
@qml.qnode(dev)
def measure_cube(Initial_State):
    qml.StatePrep(Initial_State, wires = qubits)
    return (qml.sample(wires=qubits), qml.probs()) #   sample returns e.g. [0,1,0,0,1]

# The main function - this is run every time a button is pressed 
# runs the move -> gets final state and probabilities -> under each bit value stores the vector (from state), probabilities, and polar (converts from state)
# -> calculates transparency (255 if magnitude is off) and places circles representing polar angle (if angle is on) -> place background Nauru graph
# -> place cube images with certain transparency -> place labels under cubes -> end game (if conditions meet)
def main(Ham=None, measure_option="N", time_step=1):
    global initial_state, current_image, state_dict, image_refs, background_image, step_counter, end_game # yes I know so many globals

    # Skips if just want to run image update not run another move 
    if type(Ham) != NoneType: 
        try: # For classical and quantum moves
            result, probs = general_circuit(initial_state, time_step, Ham)
            step_counter += abs(time_step) # Absolute because you can have negative time steps

        except: # For measure and reset circuits
            try:
                result, probs = Ham(initial_state)

            except Exception as e: # When that stupid bug pops up :(
                print(e)
                messagebox.showwarning(title="Whoops", message="Oh no you've found the bug Karina can't get rid of.\nShe'll get some bug spray soon. Sit tight.\nIn the meantime you can't measure this state sorry.")
                return # Breaks out of function early (or else it will keep giving errors which is annoying -> this bug prevents measurement)

        label_list[1].config(text="Number of moves: "+str(sf.round(step_counter, decimals=2))) # Update number of steps

        if measure_option == "Y": # If it was measure_circuit convert from binary to 32x1 list
            result_temp = "".join(map(str,result)) #e.g [0,0,0,0,1] -> ['0','0','0','0','1'] -> '00001'
            result_temp = int(result_temp,2) #e.g. '00001' -> 1   (input is base 2, output is integer)
            result = [0] * result_temp + [1 + 0j] + [0] * (31-result_temp) #e.g. [0] * 1 + [1] + [0] * 30 = [0,1,0,0,0,0,0,0,0,0,...,0] (integer tells us where the 1 is)

        for index,state in enumerate(result):
            state_polar = cmath.polar(state)

            try:
                state_dict[str(bin(index)[2:].zfill(5))][2] = state_polar # Store polar values in dictionary (r,theta)

            except:
                continue
        
            else:
                state_dict[str(bin(index)[2:].zfill(5))][3] = probs[index] # Store probabilities in dictionary
                state_dict[str(bin(index)[2:].zfill(5))][4] = state # Store vector values in dictionary
    
    else:
        result = initial_state

    # Delete previous images 
    image_refs = []
    canvas.delete("current_image")
    canvas.delete("circle")
    canvas.delete("Nauru_graph")
    canvas.delete("initial_text")
    canvas.delete("congrats")

    # Insert/update angle circles (if on) and/or calculate transparency depending on magnitude (this uses the polar form)
    for cube_state in state_dict:
        if state_dict[cube_state][3] >= 1e-3: # Percentage has to be greater than 0.1% (0.001 in dictionary) -> aligns with label now
            if is_on_mag == True:
                transparency = int(255 * state_dict[cube_state][2][0]) # polar (radius) ∈ [0,1] ----> polar (radius) x 255 ∈ [0,255] (this works with colour/transparency)
            else:
                transparency = 255 # Leave full transparency 

            if is_on_angle == True:
                hue = (state_dict[cube_state][2][1] / (2*np.pi)) % 1.0 # polar (angle) ∈ (-pi,pi] ----> ∈ (-0.5,0.5] ----> hue ∈ [0,1] 
                
                if col_option.get()== "Dark": lum = 0.5/255*transparency # Make circles as transparent as cubes
                else: lum = 1-0.5/255*transparency

                if lum > 0.025: # If too dark it's just a black circle which looks terrible
                    canvas.create_oval(state_dict[cube_state][0]-50, state_dict[cube_state][1]-50,state_dict[cube_state][0]+50, 
                                    state_dict[cube_state][1]+50, fill=colour.Color(hue=hue, saturation=1, luminance = lum),outline="", tags="circle")

    image_path = os.path.join(IMAGE_DIR, "honeycomb_connections_CMY.png") # os.path.join depends on the operating system
    background_image = tk.PhotoImage(file=image_path)
    canvas.create_image(750, 400, image=background_image, tags = "Nauru_graph") # Nauru graph

    # Place cube images in locations
    for cube_state in state_dict:
        if state_dict[cube_state][3] >= 1e-3: # Percentage has to be greater than 0.1% (0.001 in dictionary) -> aligns with label now

            im = Image.open(os.path.join(IMAGE_DIR, "00000.png" if cube_state == "00000" else f"{cube_state}.PNG"))
            im_resize = im.resize((im.width // 5, im.height // 5)) # This reduces the size without losing quality yay
            alpha_pixels = list(im_resize.getdata()) # Pixels

            if is_on_mag == True:
                transparency = int(255 * state_dict[cube_state][2][0]) # polar (magnitude) ∈ [0,1] ----> polar (radius) x 255 ∈ [0,255] (this works with colour/transparency)
            else:
                transparency = 255 # Leave full transparency 
            
            for index,pixel in enumerate(alpha_pixels):
                if pixel[3] != 0: # Leave already transparent pixels transparent - pixel[3] = transparent/alpha pixels
                    temp = list(alpha_pixels[index]) # Make list of RGBalpha
                    temp[3] = transparency # Make transparency value the alpha value in list 
                    alpha_pixels[index] = tuple(temp) # Put new pixel back in
                    
            im_resize.putdata(alpha_pixels) # Update pixels
            img = ImageTk.PhotoImage(im_resize)
            canvas.create_image(state_dict[cube_state][0],state_dict[cube_state][1],image=img) # Put image in!
            image_refs.append(img) # Solution to trash collecting bug (keep images as a variable or else it will forget it)

    # Place labelling on each cube
    rep_change()
    initial_state = result # Update the initial state to the current state

    # End game sequence
    if initial_state[0] == 1+0j and end_game=="Y":
        canvas.create_text(700, 400,text="CONGRATULATIONS", font=helv28, fill=colour_chose[col_option.get()], tags="congrats")
        canvas.delete("Nauru_graph")

        # Disable all buttons except reset button
        for button in button_list+radbuttons:
            button.config(state=tk.DISABLED)

        canvas.itemconfigure(toggle_button_angle, state = tk.DISABLED)
        canvas.itemconfigure(toggle_button_mag, state = tk.DISABLED)

        end_game = "N"

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

    # Extra moves (2-, 3-, and 4-cycle)
    elif event.keysym=='2':
        main(Ham2,time_step=time_step)
    elif event.keysym=='3':
        main(Ham3,time_step=time_step)
    elif event.keysym=='4':
        main(Ham4,time_step=time_step)

    # Tools
    elif event.keysym=='Return':
        reset_cube()
    elif event.keysym=='space':
        main(measure_cube, "Y")

# Function to reset the game to 100% solved state (00000)
def reset_cube():
    global initial_state, step_counter, end_game

    initial_state = [1 + 0j] + [0] * 31 

    step_counter = 0
    end_game = "N"
    window.bind('<Key>', on_key_press) # This is here if you win the game (to unlock the key functions)

    # Again only when you win the game (to unlock the frozen buttons)
    for button in button_list+radbuttons:
        button.config(state=tk.NORMAL) 
    canvas.itemconfigure(toggle_button_angle, state = tk.NORMAL)
    canvas.itemconfigure(toggle_button_mag, state = tk.NORMAL)

    main(reset_circuit) # To update the images and labels

# To label each cube either the percentage, vector or polar representation.
def rep_change():
    canvas.delete("text") 
    canvas.delete("initial_text")
    var = v.get() # var is the representation type chosen from the radiobuttons
    fill_colour = colour_chose[col_option.get()] # What font colour is the labels?

    for cube_state in state_dict:
        if state_dict[cube_state][2][0] != 0 or state_dict[cube_state][2][1] != 0:
            if var == "1": # Percentage
                label = sf.round(state_dict[cube_state][3]*100,sigfigs=3)
                if 0.1 > label >= 0.001: label = "< 0.1" # Only show percentages >0.001% and between 0.001 and 0.1 just label it <0.1%
                elif label == 100: label = 100 # Show 100.0% as 100%

                if label == "< 0.1" or label > 0.1:
                    canvas.create_text(state_dict[cube_state][0],(state_dict[cube_state][1]+60),
                                        text=str(label)+"%", 
                                        fill=fill_colour, font=math12, tags="text") # Create label (python labels this text)
                
            elif var == "2": # Vector
                label_vec = np.real_if_close((state_dict[cube_state][4])) # Eliminates super small imaginary values
                if abs(label_vec.real) >= 0.01 or abs(label_vec.imag) >= 0.01: # Only show if either the real or imaginary values are greater than 0.01
                    text = "{:.2f}".format(label_vec) # Round to 2 decimal points
                    if abs(label_vec.real) < 0.01:
                        text = "{:.2f}".format(label_vec.imag) + "i" # If just imaginary get rid of 0.00 + imag -> imag
                    canvas.create_text(state_dict[cube_state][0],(state_dict[cube_state][1]+60),
                                        text=(text.replace("(", "").replace(")", "").replace("j", "i")), 
                                        fill=fill_colour, font=math12, tags="text") # Create label (python labels this text)
                
            elif var == "3": # Polar
                label1 = "%.2f" % state_dict[cube_state][2][0] # Radius e.g. 0.3444 -> "0.34"
                label2 = Fraction(np.round(state_dict[cube_state][2][1]/pi,15)).limit_denominator() # Convert Angle to fraction and limit the denominator if the time step stuffs up
                if abs(state_dict[cube_state][2][0]) >= 0.01:
                    canvas.create_text(state_dict[cube_state][0],(state_dict[cube_state][1]+60),
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
    global initial_state, step_counter, end_game

    time_step = scale_v.get() # Get the current time step

    choice = {"R2":HamR2, "U2":HamU2, "F2":HamF2} # There are three choice for the three moves

    for _ in range(100):
        QuMove = np.random.choice(["R2", "U2", "F2"]) # Choose any of the three moves (this is a string cause it doesn't work with matrices)
        result = general_circuit(initial_state, time_step, choice[QuMove])[0] # Access only the result with [0] (else you have to do result,probs = )
        initial_state = result
    
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

    popup_path = Image.open(os.path.join(IMAGE_DIR, image))
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

# This is the GUI function and is the first to be called
def GUI():
    global initial_state, current_image, canvas, toggle_button_angle, toggle_button_mag, label_list, radbuttons, button_list


    ###########  Initialisation  ##############

    initial_state = [1 + 0j] + [0] * 31 # This starts the cube in the solved state

    # Add three extra items in the cube dictionary for the polar,percentage,vector. One dictionary item is now [posx,posy,(radius,angle),percentage,vector]
    for index,state in enumerate(initial_state):
        state_pol = cmath.polar(state)

        try: # Some states can't be accessed so try all binary numbers from 0 to 31
            state_dict[str(bin(index)[2:].zfill(5))].append(state_pol) # Polar

        except: # Skip if not available
            continue

        else:
            state_dict[str(bin(index)[2:].zfill(5))].append(np.real(state)) # Percentage
            state_dict[str(bin(index)[2:].zfill(5))].append(state) # Vector

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
    #    -> Options     
    #    -> Accessibility
    # -> Exit           
    menubar = tk.Menu(window) 
    window.config(menu=menubar)
    file_menu = tk.Menu(menubar, tearoff=False)
    help_menu = tk.Menu(menubar,tearoff=False)

    sub_menu = tk.Menu(file_menu, tearoff=False)
    sub_menu.add_command(label='Key Options', command=lambda: preferences("options")) # Use lambda to specify a parameter in a function
    sub_menu.add_command(label='Colour Options', command=lambda: preferences("colour_change"))

    file_menu.add_cascade(label="Preferences", menu=sub_menu)
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=window.destroy)
    menubar.add_cascade(label="File", menu=file_menu)

    # help_menu.add_command(label="About")
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
    image_path = os.path.join(IMAGE_DIR, "honeycomb_connections_CMY.png")
    background_image = tk.PhotoImage(file=image_path)
    canvas.create_image(750, 400, image=background_image, tags="Nauru_graph")

    # Solved state cube image
    im = Image.open(os.path.join(IMAGE_DIR, "00000.png"))
    im_resize = im.resize((im.width // 5, im.height // 5))
    current_image = ImageTk.PhotoImage(im_resize)
    canvas.create_image(state_dict["00000"][0],state_dict["00000"][1],image=current_image, tags="current_image")
    
    # Cube label
    canvas.create_text(state_dict["00000"][0],(state_dict["00000"][1]+60), text="100%", fill="white", font=("Cambria Math",12,"bold"), tags="initial_text")

    # Rainbow image for quantum scramble button
    rainbow = Image.open(os.path.join(IMAGE_DIR, "rainbow.png"))
    rainbow_resize = rainbow.resize((150,60))
    rainbow = ImageTk.PhotoImage(rainbow_resize)

    # Clockwise and anticlockwise image to go on top of QuR2 buttons to indicate move and inverse move
    anti_clock = Image.open(os.path.join(IMAGE_DIR, "anti_clock.png"))
    anti_clock_resize = anti_clock.resize((anti_clock.width//10, anti_clock.height//10))
    anti_clock = ImageTk.PhotoImage(anti_clock_resize)
    clock = Image.open(os.path.join(IMAGE_DIR, "clock.png"))
    clock_resize = clock.resize((40,40))
    clock = ImageTk.PhotoImage(clock_resize)

    canvas.create_image(330,250,image=anti_clock)
    canvas.create_image(200,250,image=clock)

    # On and Off button for the magnitude and angle buttons
    on = Image.open(os.path.join(IMAGE_DIR, "toggle_on.png"))
    off = Image.open(os.path.join(IMAGE_DIR, "toggle_off.png"))
    on_image = ImageTk.PhotoImage(on.resize((on.width // 16, on.height // 16)))
    off_image = ImageTk.PhotoImage(off.resize((on.width // 16, on.height // 16)))
    canvas.on_image = on_image
    canvas.off_image = off_image
    toggle_button_angle = canvas.create_image(1210, 650, image = off_image)
    toggle_button_mag = canvas.create_image(1210, 700, image = on_image)

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
                    command=lambda: main(measure_cube, "Y"))
    
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
    angle = canvas.create_text(1125,650, text="Angle", font=("Helvetica",12,"bold"), fill="white") # Angle text
    mag = canvas.create_text(1108,700, text="Magnitude", font=("Helvetica",12,"bold"), fill="white") # Magnitude text

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
