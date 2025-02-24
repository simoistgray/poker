import pickle
import tkinter as tk
from datetime import datetime
from tkinter import messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

current_canvas = None
current_player = None
imagedata = {
    "Simon": "simon.jpg"
}


def load_data(filename="poker_data.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


def save_data(data, filename="poker_data.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(data, f)


def add_player():
    data = load_data()
    player_name = player_name_entry.get()
    if player_name not in data:
        data[player_name] = [{'date': '2024-09-06', 'buy_in': 0.0, 'cash_out': 0.0, 'rebuys': 0}]  # Initialize with an empty session list
        player_name_entry.delete(0, tk.END)
        show_log_data()
        save_data(data)
    else:
        messagebox.showwarning("Input Error", "Please enter a new player name.")


def add_session_data():
    player_name = player_dropdown_var.get()
    buy_in = buy_in_entry.get()
    cash_out = cash_out_entry.get()
    date = date_entry.get()
    rebuys = rebuy_entry.get()
    data = load_data()

    if player_name and buy_in and cash_out and date:
        session = {"date": date, "buy_in": float(buy_in), "cash_out": float(cash_out), "rebuys": int(rebuys)}
        data[player_name].append(session)
        messagebox.showinfo("Success", f"Data added for '{player_name}'!")
        buy_in_entry.delete(0, tk.END)
        buy_in_entry.insert(0, "15")
        cash_out_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        rebuy_entry.delete(0, tk.END)
        rebuy_entry.insert(0, "0")
        show_log_data()
        save_data(data)
    else:
        messagebox.showwarning("Input Error", "Please fill all fields.")


def update_player_dropdown(data):
    player_dropdown["menu"].delete(0, "end")  # Clear existing entries
    for player in data.keys():
        player_dropdown["menu"].add_command(label=player, command=tk._setit(player_dropdown_var, player))


def show_main_menu():
    hide_all_frames()
    main_menu_frame.pack(expand=True, pady=20)
    root.update_idletasks()
    root.focus_force()


def show_log_data():
    hide_all_frames()
    log_frame.pack(expand=True, pady=20)
    root.update_idletasks()
    root.focus_force()


def show_overall_view():
    hide_all_frames()
    set_general_dimensions(650, 350)
    view_frame.pack(expand=True, pady=20)
    root.focus_force()
    root.update_idletasks()


def show_overall_view_from_player():
    clear_frame(stats_frame)
    # clear_frame(image_frame)
    root.update_idletasks()
    show_overall_view()


def show_overall_view_from_general():
    clear_frame(general_view_frame)
    root.update_idletasks()
    show_overall_view()


def show_add_data():
    hide_all_frames()
    set_general_dimensions(650, 430)
    update_player_dropdown(load_data())  # Update dropdown with player list
    add_data_frame.pack(expand=True, pady=20)
    root.update_idletasks()
    root.focus_force()


def show_add_player():
    hide_all_frames()
    add_player_frame.pack(expand=True, pady=20)
    root.update_idletasks()
    root.focus_force()


def show_player_selection():
    dialog = tk.Toplevel(root)
    dialog.title("Select Player")
    window_width = 300
    window_height = 120
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")

    tk.Label(dialog, text="Please select a player:", font=("Press Start 2P", 12)).pack(expand=True, pady=10)

    selected_player = tk.StringVar(dialog)
    selected_player.set("Select a player")
    global player_dropdown
    player_dropdown = tk.OptionMenu(dialog, selected_player, *data.keys())
    player_dropdown.pack(expand=True, pady=5)

    def confirm_selection():
        if selected_player.get() == "Select a player":
            messagebox.showwarning("Warning", "Please select a player.")
        else:
            print(f"Player selected: {selected_player.get()}")
            show_player_view(selected_player.get())
            dialog.destroy()

    tk.Button(dialog, text="OK", command=confirm_selection).pack(expand=True, pady=10)
    root.update_idletasks()


def calculate_statistics(player_name):
    sessions = data[player_name]
    total_games = len(sessions) - 1
    total_buy_in = round(sum(session["buy_in"] for session in sessions), 2)
    total_cash_out = round(sum(session["cash_out"] for session in sessions), 2)
    low = 9999
    high = -10000
    total_net_earnings = 0
    for session in sessions:
        total_net_earnings += session["cash_out"] - session["buy_in"]
        if total_net_earnings > high:
            high = round(total_net_earnings, 2)
            high_date = session["date"]
        if total_net_earnings < low:
            low = round(total_net_earnings, 2)
            low_date = session["date"]
    if low < 0:
        low_point = f"-${low * -1}"
    else:
        low_point = f"${low}"
    total_net_earnings = round(total_net_earnings, 2)
    win_rate = sum(1 for session in sessions if
                   session["cash_out"] > session["buy_in"]) / total_games * 100 if total_games > 0 else 0

    return {
        "Total Games": total_games,
        "Total Buy-Ins": f"${total_buy_in}",
        "Total Cash Outs": f"${total_cash_out}",
        "Total Net Earnings": f"${total_net_earnings}",
        "Low Point": low_point + f" on {low_date}",
        "High Point": f"${high} on {high_date}",
        "Win Rate": f"{win_rate:.1f}%"
    }


def show_player_view(player):
    global current_canvas, current_player
    hide_all_frames()
    set_general_dimensions(950, 400)
    try:
        player_image = Image.open(imagedata[player])
    except:
        player_image = Image.open("question.jpg")

    player_image = player_image.resize((100, 100))
    player_photo = ImageTk.PhotoImage(player_image)
    name_label.config(text=player, font=("Press Start 2P", 16, "bold"))
    name_label.pack()
    player_image_label.config(image=player_photo)
    player_image_label.pack(expand=True, pady=5)
    image_frame.photo = player_photo  # Keep reference to image

    def plot_earnings(player_name):
        dates = [datetime.strptime(session["date"], "%Y-%m-%d") for session in data[player_name]]
        newDates = []
        for date in dates:
            newDates.append(str(date)[5:11])
        net_earnings = [session["cash_out"] - session["buy_in"] for session in data[player_name]]
        new_net_earnings = []
        so_far = 0
        for x in net_earnings:
            if net_earnings.index(x) != 0:
                entry = x
                so_far += entry
                new_net_earnings.append(so_far)
            else:
                new_net_earnings.append(x)

        fig, ax = plt.subplots(figsize=(5, 3))
        fig.patch.set_facecolor('#2E2E2E')  # Dark gray background
        ax.set_facecolor('#3E3E3E')  # Slightly lighter gray for axes

        for i in range(1, len(new_net_earnings)):
            color = "green" if new_net_earnings[i] - new_net_earnings[i - 1] >= 0 else "red"
            ax.plot(newDates[i - 1:i + 1], new_net_earnings[i - 1:i + 1], marker="o", color=color, linestyle="-")

        ax.set_title(f"Earnings Over Time for {player_name}", color="white")
        ax.set_xlabel("Date", color="white")
        ax.set_ylabel("Net Earnings", color="white")
        ax.tick_params(axis="x", rotation=45, colors='white')
        ax.tick_params(axis="y", colors='white')
        fig.tight_layout()
        return fig

    earnings_fig = plot_earnings(player)
    if current_canvas is not None:
        if current_player != player:
            current_canvas.get_tk_widget().destroy()
            current_canvas = FigureCanvasTkAgg(earnings_fig, master=info_frame)
            current_canvas.draw()
    elif current_canvas is None:
        current_canvas = FigureCanvasTkAgg(earnings_fig, master=info_frame)
        current_canvas.draw()

    current_player = player

    current_canvas.get_tk_widget().pack(expand=True, side="top", pady=10)

    root.update_idletasks()

    def display_player_statistics(player_name):
        stats = calculate_statistics(player_name)
        for stat, value in stats.items():
            tk.Label(stats_frame, text=f"{stat}: {value}", font=("Press Start 2P", 12)).pack(anchor="w")

    display_player_statistics(player)

    player_view_frame.pack(expand=True)
    id_card_frame.pack(fill="x")
    content_frame.pack(fill="x")
    image_frame.grid(row=0, column=0, sticky="n")
    info_frame.grid(row=0, column=1, sticky="n", padx=20)
    stats_frame.pack(expand=True, side="bottom")
    root.update_idletasks()
    root.focus_force()


def show_general_view():
    global current_canvas, current_player
    data = load_data()
    hide_all_frames()
    set_general_dimensions(1050, 550)
    tk.Label(general_view_frame, text="General Overview", font=title_font).pack(expand=True, pady=10)
    tk.Button(general_view_frame, text="Back", font=small_button_font, command=show_overall_view_from_general).pack(expand=True, pady=15)
    earnings_data = {}
    for player in data.keys():
        dates = [datetime.strptime(session["date"], "%Y-%m-%d") for session in data[player]]
        net_earnings = [session["cash_out"] - session["buy_in"] for session in data[player]]
        new_net_earnings = []
        so_far = 0
        for x in net_earnings:
            if net_earnings.index(x) != 0:
                entry = x
                so_far += entry
                new_net_earnings.append(so_far)
            else:
                new_net_earnings.append(x)
        earnings_data[player] = (dates, new_net_earnings)

    earnings_fig = plot_all_earnings(earnings_data)
    if current_canvas is not None:
        if current_player != "general":  # Only update if the player has changed
            current_canvas.get_tk_widget().destroy()
        current_canvas = FigureCanvasTkAgg(earnings_fig, master=general_view_frame)
        current_canvas.draw()
    elif current_canvas is None:
        current_canvas = FigureCanvasTkAgg(earnings_fig, master=general_view_frame)
        current_canvas.draw()

    current_player = "general"

    current_canvas.get_tk_widget().pack(expand=True, side="bottom", pady=10)

    legend_labels = list(earnings_data.keys())
    for i, player in enumerate(legend_labels):
        tk.Label(general_view_frame, text=player, bg='white', font=("Press Start 2P", 12)).pack(anchor="w")

    root.update_idletasks()

    general_view_frame.pack(expand=True, pady=20)
    root.update_idletasks()
    root.focus_force()


def show_stats():
    hide_all_frames()
    set_general_dimensions(700, 360)

    biggest_winner_player = ""
    biggest_winner_total = 0
    biggest_loser_player = ""
    biggest_loser_total = 0
    most_degenerate_player = ""
    most_buyins = 0
    highest_win_rate_player = ""
    highest_win_rate = -100
    best_night_date = ""
    best_night_player = ""
    best_night_total = 0
    worst_night_date = ""
    worst_night_player = ""
    worst_night_total = 100000
    days = {}
    total_wagered = 0

    for player in data:
        sessions = data[player]
        total_games = len(sessions) - 1
        total_net_earnings = round(sum(session["cash_out"] - session["buy_in"] for session in sessions), 2)
        wins = 0
        rebuys = sum(session["rebuys"] for session in sessions)
        if total_net_earnings > biggest_winner_total:
            biggest_winner_total = total_net_earnings
            biggest_winner_player = player
        if total_net_earnings < biggest_loser_total:
            biggest_loser_total = total_net_earnings
            biggest_loser_player = player
        if rebuys > most_buyins:
            most_degenerate_player = player
            most_buyins = rebuys
        for session in data[player]:
            total_wagered += session["buy_in"]
            try:
                days[session["date"]] = days[session["date"]] + session["buy_in"]
            except:
                days[session["date"]] = session["buy_in"]
            if session["cash_out"] > session["buy_in"]:
                print(player, session["date"], session["cash_out"] - session["buy_in"], total_games)
                wins += 1
            if session["cash_out"] - session["buy_in"] > best_night_total:
                best_night_total = round(session["cash_out"] - session["buy_in"], 2)
                best_night_player = player
                best_night_date = session["date"]
            if session["cash_out"] - session["buy_in"] < worst_night_total:
                worst_night_total = round(session["cash_out"] - session["buy_in"], 2)
                worst_night_player = player
                worst_night_date = session["date"]
        win_rate = round((wins / total_games), 2)
        # print(player, win_rate)
        if win_rate > highest_win_rate and total_games > 3:
            highest_win_rate_player = player
            highest_win_rate = win_rate

    max_date, max_value = max(days.items(), key=lambda x: x[1])
    biggest_winner_label.pack(fill='x', anchor='w')
    biggest_winner_label.config(text=f"Biggest Winner: {biggest_winner_player} (${biggest_winner_total:.2f})",
                                fg='gold')
    biggest_loser_label.pack(fill='x', anchor='w')
    biggest_loser_label.config(text=f"Biggest Loser: {biggest_loser_player} (${biggest_loser_total:.2f})", fg='red')
    most_degenerate_label.pack(fill='x', anchor='w')
    most_degenerate_label.config(text=f"Most Degenerate Gambler: {most_degenerate_player} (Rebuys: {most_buyins})",
                                 fg='orange')
    highest_win_rate_label.pack(fill='x', anchor='w')
    highest_win_rate_label.config(text=f"Highest Win Rate: {highest_win_rate_player} ({highest_win_rate:.2%})",
                                  fg='cyan')
    best_night_label.pack(fill='x', anchor='w')
    best_night_label.config(text=f"Best Night: {best_night_player} on {best_night_date} (${best_night_total:.2f})",
                            fg='green')
    worst_night_label.pack(fill='x', anchor='w')
    worst_night_label.config(text=f"Worst Night: {worst_night_player} on {worst_night_date} (${worst_night_total:.2f})",
                             fg='red')
    total_wagered_label.pack(fill='x', anchor='w')
    total_wagered_label.config(text=f"Total Wagered: ${total_wagered:.2f}",
                             fg='white')

    biggest_night_label.pack(fill='x', anchor='w')
    biggest_night_label.config(text=f"Biggest Night: {max_date} (${max_value:.2f})", fg='light green')
    biggest_winner_label.pack(expand=True, pady=5)
    biggest_loser_label.pack(expand=True, pady=5)
    most_degenerate_label.pack(expand=True, pady=5)
    highest_win_rate_label.pack(expand=True, pady=5)
    best_night_label.pack(expand=True, pady=5)
    worst_night_label.pack(expand=True, pady=5)
    biggest_night_label.pack(expand=True, pady=5)
    champions_frame.pack(expand=True, pady=20)
    root.update_idletasks()
    root.focus_force()


def plot_all_earnings(earnings_data):
    fig, ax = plt.subplots(figsize=(10, 4))

    fig.patch.set_facecolor('#2E2E2E')  # Dark gray background
    ax.set_facecolor('#3E3E3E')  # Slightly lighter gray for axes

    for player, (dates, net_earnings) in earnings_data.items():
        ax.plot(dates, net_earnings, marker='o', linestyle='-', label=player)

    ax.set_title("Earnings Over Time for All Players", color='white')
    ax.set_xlabel("Date", color='white')
    ax.set_ylabel("Net Earnings", color='white')
    ax.axhline(0, color='white', linestyle='--', linewidth=1)

    ax.tick_params(axis="x", rotation=45, colors='white')  # X-axis ticks color
    ax.tick_params(axis="y", colors='white')  # Y-axis ticks color

    ax.legend(facecolor='#3E3E3E', edgecolor='white', loc="best", ncol=5)
    plt.subplots_adjust(bottom=0.25)
    fig.tight_layout()

    return fig


def exit_program():
    plt.close('all')
    root.destroy()


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()
    root.update_idletasks()


def hide_all_frames():
    set_general_dimensions()
    frames = [main_menu_frame, view_frame, log_frame, add_data_frame, add_player_frame, player_view_frame,
              general_view_frame, id_card_frame, stats_frame, content_frame, image_frame, champions_frame]
    for frame in frames:
        frame.pack_forget()
    root.update_idletasks()


def set_general_dimensions(window_width=650, window_height=440):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")


def init():
    frames = []
    global data
    data = load_data()
    global root
    root = tk.Tk()
    root.title("Simon's Awesome Poker Winnings Tracker")

    set_general_dimensions()

    global title_font, button_font, small_button_font, stat_font
    title_font = ("Press Start 2P", 35, "bold")
    button_font = ("Press Start 2P", 25)
    small_button_font = ("Press Start 2P", 10)
    stat_font = ("Press Start 2P", 15)

    def main_menu_frame_init():
        global main_menu_frame
        main_menu_frame = tk.Frame(root)
        frames.append(main_menu_frame)
        title_label = tk.Label(main_menu_frame, text="Poker Winnings", font=title_font)
        title_label.pack(expand=True, pady=10)

        log_data_button = tk.Button(main_menu_frame, text="Log Data", font=button_font, command=show_log_data)
        log_data_button.pack(expand=True, pady=15)

        overall_view_button = tk.Button(main_menu_frame, text="Overall View", font=button_font, command=show_overall_view)
        overall_view_button.pack(expand=True, pady=15)

        champions_button = tk.Button(main_menu_frame, text="The Best (and Worst)", font=button_font, command=show_stats)
        champions_button.pack(expand=True, pady=15)

        exit_button = tk.Button(main_menu_frame, text="Exit", font=button_font, command=exit_program)
        exit_button.pack(expand=True, pady=15)

        main_menu_frame.pack(expand=True, pady=10)

    def log_data_frame_init():
        global log_frame
        log_frame = tk.Frame(root)
        frames.append(log_frame)
        tk.Label(log_frame, text="Log Data", font=title_font).pack(expand=True, pady=10)
        tk.Button(log_frame, text="Add Data for a Player", font=button_font, command=show_add_data).pack(expand=True,
                                                                                                         pady=15)
        tk.Button(log_frame, text="Add a New Player", font=button_font, command=show_add_player).pack(expand=True, pady=15)
        tk.Button(log_frame, text="Back", font=button_font, command=show_main_menu).pack(expand=True, pady=15)

    def add_data_frame_init():
        global add_data_frame
        add_data_frame = tk.Frame(root)
        frames.append(add_data_frame)
        tk.Label(add_data_frame, text="Add Data for a Player", font=("Press Start 2P", 25, "bold")).pack(expand=True,
                                                                                                         pady=5)

        global player_dropdown_var, date_entry, buy_in_entry, cash_out_entry, rebuy_entry, player_dropdown
        player_dropdown_var = tk.StringVar(add_data_frame)
        player_dropdown_var.set("Select a player")
        player_dropdown = tk.OptionMenu(add_data_frame, player_dropdown_var, data.keys())
        player_dropdown.pack(expand=True, pady=5)

        tk.Label(add_data_frame, text="Date:", font=("Press Start 2P", 14)).pack(expand=True, pady=5)
        date_entry = tk.Entry(add_data_frame)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.pack(expand=True)

        tk.Label(add_data_frame, text="Buy-In:", font=("Press Start 2P", 14)).pack(expand=True, pady=5)
        buy_in_entry = tk.Entry(add_data_frame)
        buy_in_entry.insert(0, "15")
        buy_in_entry.pack(expand=True)

        tk.Label(add_data_frame, text="Cash-Out:", font=("Press Start 2P", 14)).pack(expand=True, pady=5)
        cash_out_entry = tk.Entry(add_data_frame)
        cash_out_entry.pack(expand=True)

        tk.Label(add_data_frame, text="Rebuys:", font=("Press Start 2P", 14)).pack(expand=True, pady=5)
        rebuy_entry = tk.Entry(add_data_frame)
        rebuy_entry.insert(0, "0")
        rebuy_entry.pack(expand=True)

        tk.Button(add_data_frame, text="Submit", font=small_button_font, command=add_session_data).pack(expand=True, pady=5)
        tk.Button(add_data_frame, text="Back", font=small_button_font, command=show_log_data).pack(expand=True, pady=5)

    def add_player_frame_init():
        global add_player_frame, player_name_entry
        add_player_frame = tk.Frame(root)
        frames.append(add_player_frame)
        tk.Label(add_player_frame, text="Add a New Player", font=title_font).pack(expand=True, pady=10)

        tk.Label(add_player_frame, text="Player Name:", font=("Press Start 2P", 14)).pack(expand=True, pady=5)
        player_name_entry = tk.Entry(add_player_frame)
        player_name_entry.pack(expand=True, pady=5)

        tk.Button(add_player_frame, text="Add Player", font=button_font, command=add_player).pack(expand=True, pady=5)
        tk.Button(add_player_frame, text="Back", font=button_font, command=show_log_data).pack(expand=True, pady=5)

    def overall_view_frame_init():
        global view_frame
        view_frame = tk.Frame(root)
        frames.append(view_frame)
        tk.Label(view_frame, text="Overall View", font=title_font).pack(expand=True, pady=10)
        tk.Button(view_frame, text="Player View", font=button_font, command=show_player_selection).pack(expand=True,
                                                                                                        pady=15)
        tk.Button(view_frame, text="General Overview", font=button_font, command=show_general_view).pack(expand=True,
                                                                                                         pady=15)
        tk.Button(view_frame, text="Back", font=button_font, command=show_main_menu).pack(expand=True, pady=15)

    def player_view_frame_init():
        global player_view_frame
        player_view_frame = tk.Frame(root)
        frames.append(player_view_frame)
        tk.Label(player_view_frame, text="Player View", font=title_font).pack(expand=True, pady=10)
        tk.Button(player_view_frame, text="Back", font=small_button_font, command=show_overall_view_from_player).pack(
            expand=True)

    def id_card_frame_init():
        global id_card_frame
        id_card_frame = tk.Frame(player_view_frame)
        id_card_frame.pack(fill="x")

    def content_frame_init():
        global content_frame
        content_frame = tk.Frame(id_card_frame)
        content_frame.pack(fill="x")

    def image_frame_init():
        global image_frame, name_label, player_image_label
        image_frame = tk.Frame(content_frame)
        player_image_label = tk.Label(image_frame)
        name_label = tk.Label(image_frame, text="", font=("Press Start 2P", 16, "bold"))
        image_frame.grid(row=0, column=0, sticky="n")

    def info_frame_init():
        global info_frame
        info_frame = tk.Frame(content_frame)
        info_frame.grid(row=0, column=1, sticky="n", padx=20)

    def stats_frame_init():
        global stats_frame
        stats_frame = tk.Frame(image_frame)
        stats_frame.pack(expand=True, side="bottom")

    def champions_frame_init():
        global champions_frame
        champions_frame = tk.Frame(root)
        tk.Label(champions_frame, text="The Best (and Worst)", font=button_font).pack(expand=True, pady=10)
        global biggest_winner_label, biggest_loser_label, most_degenerate_label, highest_win_rate_label, \
            best_night_label, worst_night_label, biggest_night_label, total_wagered_label
        biggest_winner_label = tk.Label(champions_frame, text="", font=stat_font)
        biggest_loser_label = tk.Label(champions_frame, text="", font=stat_font)
        most_degenerate_label = tk.Label(champions_frame, text="", font=stat_font)
        highest_win_rate_label = tk.Label(champions_frame, text="", font=stat_font)
        best_night_label = tk.Label(champions_frame, text="", font=stat_font)
        worst_night_label = tk.Label(champions_frame, text="", font=stat_font)
        biggest_night_label = tk.Label(champions_frame, text="", font=stat_font)
        total_wagered_label = tk.Label(champions_frame, text="", font=stat_font)
        tk.Button(champions_frame, text="Back", font=small_button_font, command=show_main_menu).pack(expand=True)

    def general_view_frame_init():
        global general_view_frame
        general_view_frame = tk.Frame(root)
        frames.append(general_view_frame)

    def run():
        main_menu_frame_init()
        log_data_frame_init()
        add_data_frame_init()
        add_player_frame_init()
        overall_view_frame_init()
        player_view_frame_init()
        id_card_frame_init()
        content_frame_init()
        image_frame_init()
        info_frame_init()
        stats_frame_init()
        champions_frame_init()
        general_view_frame_init()

    run()
    root.mainloop()


init()
