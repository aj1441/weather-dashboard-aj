"""Interactive historical analysis window for bulk history across one or more cities"""

import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import List, Dict, Optional
from datetime import datetime

# Lazy import matplotlib to avoid display issues until needed
MATPLOTLIB_AVAILABLE = False
plt = None
FigureCanvasTkAgg = None
Figure = None
NavigationToolbar2Tk = None
sns = None
np = None
mplcursors = None


def _import_matplotlib():
    global MATPLOTLIB_AVAILABLE, plt, FigureCanvasTkAgg, Figure, NavigationToolbar2Tk, sns, np, mplcursors
    if MATPLOTLIB_AVAILABLE:
        return True
    try:
        import matplotlib
        matplotlib.use('TkAgg')
        import matplotlib.pyplot as plt  # type: ignore
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # type: ignore
        from matplotlib.figure import Figure  # type: ignore
        import seaborn as sns  # type: ignore
        import numpy as np  # type: ignore
        try:
            import mplcursors as mplc
        except Exception:
            mplc = None
        MATPLOTLIB_AVAILABLE = True
        globals()['plt'] = plt
        globals()['FigureCanvasTkAgg'] = FigureCanvasTkAgg
        globals()['NavigationToolbar2Tk'] = NavigationToolbar2Tk
        globals()['Figure'] = Figure
        globals()['sns'] = sns
        globals()['np'] = np
        globals()['mplcursors'] = mplc
        return True
    except Exception:
        return False


class HistoricalAnalysisWindow(tb.Toplevel):
    """A separate window to run interactive historical analyses across cities."""

    def __init__(
        self,
        parent: tk.Misc,
        db,
        cities_with_data: List[Dict],
        preselected_cities: Optional[List[str]] = None,
    ) -> None:
        super().__init__(parent)
        self.title("Historical Analysis")
        self.geometry("1100x700")
        self.db = db
        self.cities_with_data = cities_with_data or []
        self.preselected_cities = set(preselected_cities or [])

        # State
        self.chart_type_var = tb.StringVar(value="Seasonal Trend Explorer")
        self.season_var = tb.StringVar(value="Summer")  # for seasonal trends
        self.trendline_var = tb.BooleanVar(value=True)
        self.rolling_window_var = tb.IntVar(value=3)
        self.event_hot_var = tb.BooleanVar(value=True)
        self.event_rain_var = tb.BooleanVar(value=True)
        self.event_wind_var = tb.BooleanVar(value=False)
        self.event_cold_var = tb.BooleanVar(value=False)

        # Build UI
        self._build_layout()

    def _build_layout(self) -> None:
        # Top controls frame
        top = tb.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=12, pady=8)

        # Chart type
        tb.Label(top, text="Chart Type:", font=("Helvetica Neue", 10, "bold")).grid(row=0, column=0, sticky="w")
        self.chart_combo = tb.Combobox(top, textvariable=self.chart_type_var, state="readonly", width=30)
        self.chart_combo['values'] = [
            "Seasonal Trend Explorer",
            "Extreme Weather Frequency",
            "Monthly Deviation Heatmap",
        ]
        self.chart_combo.grid(row=1, column=0, sticky="w", padx=(0, 12))
        self.chart_combo.bind('<<ComboboxSelected>>', self._on_chart_type_changed)

        # Dynamic options frame
        self.options_frame = tb.Labelframe(top, text="Options", bootstyle="secondary")
        self.options_frame.grid(row=0, column=1, rowspan=2, sticky="ew", padx=12)
        self.options_frame.columnconfigure(0, weight=1)
        self._rebuild_options()

        # City selector frame with checkboxes
        self.city_frame = tb.Labelframe(self, text="Cities", bootstyle="info")
        self.city_frame.pack(side=tk.LEFT, fill=tk.Y, padx=12, pady=(0, 12))
        self._build_city_selector(self.city_frame)

        # Action buttons
        actions = tb.Frame(self.city_frame)
        actions.pack(fill=tk.X, pady=(4, 6))
        tb.Button(actions, text="Select All", command=self._select_all_cities, bootstyle="secondary").pack(side=tk.LEFT)
        tb.Button(actions, text="Clear", command=self._clear_all_cities, bootstyle="secondary").pack(side=tk.LEFT, padx=(6, 0))
        tb.Button(actions, text="Generate Chart", command=self._on_generate, bootstyle="primary").pack(side=tk.RIGHT)

        # Helper label
        self.helper_label = tb.Label(self.city_frame, text="Please select at least one city for analysis.", bootstyle="warning")
        self.helper_label.pack(fill=tk.X, pady=(0, 6))

        # Chart area
        self.chart_container = tb.Labelframe(self, text="Chart", bootstyle="primary")
        self.chart_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 12), pady=(0, 12))

        # Initialize empty chart canvas
        self.figure: Optional[Figure] = None
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.toolbar_widget: Optional[NavigationToolbar2Tk] = None

    def _on_chart_type_changed(self, event=None) -> None:
        self._rebuild_options()
        # Auto-generate if there are selected cities
        if any(var.get() for var in getattr(self, 'city_vars', {}).values()):
            self._render_chart(self.chart_type_var.get(), self._get_selected_cities())

    def _rebuild_options(self) -> None:
        # Clear options
        for w in self.options_frame.winfo_children():
            w.destroy()

        chart_type = self.chart_type_var.get()
        if chart_type == "Seasonal Trend Explorer":
            tb.Label(self.options_frame, text="Season:").grid(row=0, column=0, sticky="w")
            tb.Combobox(self.options_frame, textvariable=self.season_var, state="readonly", values=["Winter","Spring","Summer","Fall"], width=12).grid(row=0, column=1, sticky="w", padx=(6, 0))
            tb.Checkbutton(self.options_frame, text="Show 3-yr rolling average", variable=self.trendline_var, bootstyle="info-round-toggle").grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
            tb.Label(self.options_frame, text="Rolling window (years):").grid(row=2, column=0, sticky="w", pady=(6, 0))
            tb.Spinbox(self.options_frame, from_=2, to=10, textvariable=self.rolling_window_var, width=5).grid(row=2, column=1, sticky="w")
        elif chart_type == "Extreme Weather Frequency":
            tb.Label(self.options_frame, text="Events:").grid(row=0, column=0, sticky="w")
            tb.Checkbutton(self.options_frame, text="Hot Days > 100°F", variable=self.event_hot_var).grid(row=1, column=0, sticky="w")
            tb.Checkbutton(self.options_frame, text="Rain > 1 inch", variable=self.event_rain_var).grid(row=2, column=0, sticky="w")
            tb.Checkbutton(self.options_frame, text="Wind Gusts > 30 mph", variable=self.event_wind_var).grid(row=3, column=0, sticky="w")
            tb.Checkbutton(self.options_frame, text="Cold Days < 32°F", variable=self.event_cold_var).grid(row=4, column=0, sticky="w")
        elif chart_type == "Monthly Deviation Heatmap":
            tb.Label(self.options_frame, text="Shows deviation from each month's long-term average per city.").grid(row=0, column=0, sticky="w")

    def _build_city_selector(self, parent: tk.Misc) -> None:
        # Scrollable checkbox list
        container = tb.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, pady=(6, 6))

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = tb.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        self.checkbox_frame = tb.Frame(canvas)

        self.checkbox_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        window_id = canvas.create_window((0, 0), window=self.checkbox_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        def _on_configure(event):
            canvas.itemconfig(window_id, width=event.width)
        canvas.bind('<Configure>', _on_configure)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Populate checkboxes
        self.city_vars: Dict[str, tk.BooleanVar] = {}
        sorted_names = sorted([c['display_name'] for c in self.cities_with_data])
        for name in sorted_names:
            var = tk.BooleanVar(value=(name in self.preselected_cities))
            self.city_vars[name] = var
            tb.Checkbutton(self.checkbox_frame, text=name, variable=var, command=self._on_city_toggle).pack(anchor='w')

    def _on_city_toggle(self) -> None:
        # Live update chart when city selection changes and at least one city is selected
        if any(var.get() for var in self.city_vars.values()):
            self._render_chart(self.chart_type_var.get(), self._get_selected_cities())

    def _select_all_cities(self) -> None:
        for var in self.city_vars.values():
            var.set(True)

    def _clear_all_cities(self) -> None:
        for var in self.city_vars.values():
            var.set(False)

    def _get_selected_cities(self) -> List[Dict]:
        names = [name for name, var in self.city_vars.items() if var.get()]
        selected: List[Dict] = []
        for name in names:
            city = next((c for c in self.cities_with_data if c['display_name'] == name), None)
            if city:
                selected.append(city)
        return selected

    def _on_generate(self) -> None:
        selected = self._get_selected_cities()
        if not selected:
            self.helper_label.configure(text="Please select at least one city for analysis.", bootstyle="warning")
            return
        self.helper_label.configure(text=f"Selected {len(selected)} city/cities.", bootstyle="secondary")
        self._render_chart(self.chart_type_var.get(), selected)

    def _reset_canvas(self) -> None:
        if not _import_matplotlib():
            return
        # Destroy previous canvas and toolbar
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if getattr(self, 'toolbar_widget', None) is not None:
            try:
                self.toolbar_widget.destroy()
            except Exception:
                pass
            self.toolbar_widget = None
        # Create new figure and canvas
        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # Add toolbar
        self.toolbar_widget = NavigationToolbar2Tk(self.canvas, self.chart_container)
        self.toolbar_widget.update()

    # ---------- Chart renderers ----------

    def _render_chart(self, chart_type: str, cities: List[Dict]) -> None:
        if chart_type == "Seasonal Trend Explorer":
            self._render_seasonal_trend(cities)
        elif chart_type == "Extreme Weather Frequency":
            self._render_extreme_events(cities)
        elif chart_type == "Monthly Deviation Heatmap":
            self._render_monthly_deviation(cities)

    def _render_seasonal_trend(self, cities: List[Dict]) -> None:
        if not _import_matplotlib():
            return
        self._reset_canvas()
        ax = self.figure.add_subplot(111)

        season = self.season_var.get()
        start = '2010-01-01'
        end = datetime.now().strftime('%Y-%m-%d')

        lines = []
        # Query and plot one line per city for the chosen season
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for city in cities:
                cursor.execute(
                    """
                    SELECT date, temperature_mean FROM historical_weather
                    WHERE city = ? AND state = ? AND date BETWEEN ? AND ?
                    """,
                    (city['city'], city['state'], start, end)
                )
                rows = cursor.fetchall()
                if not rows:
                    continue
                # Build seasonal averages by year
                import pandas as pd  # local import to avoid global overhead
                df = pd.DataFrame(rows)
                # rows are likely sqlite Row; create columns
                df.columns = [col[0] for col in cursor.description]
                df['date'] = pd.to_datetime(df['date'])
                df = df.dropna(subset=['temperature_mean'])
                df['year'] = df['date'].dt.year
                month = df['date'].dt.month
                season_map = (
                    month.isin([12, 1, 2]).map({True: 'Winter', False: None}).fillna(
                        month.isin([3, 4, 5]).map({True: 'Spring', False: None})
                    ).fillna(
                        month.isin([6, 7, 8]).map({True: 'Summer', False: None})
                    ).fillna('Fall')
                )
                df['season'] = season_map
                sdf = df[df['season'] == season]
                if sdf.empty:
                    continue
                y = sdf.groupby('year')['temperature_mean'].mean().sort_index()
                line, = ax.plot(y.index, y.values, label=city['display_name'], picker=True, pickradius=5)
                lines.append(line)
                # Optional rolling average
                if self.trendline_var.get():
                    k = max(2, int(self.rolling_window_var.get()))
                    yroll = y.rolling(window=k, min_periods=1).mean()
                    ax.plot(yroll.index, yroll.values, linestyle='--', alpha=0.5)

        ax.set_title(f"Seasonal Trend: {season}")
        ax.set_xlabel("Year")
        ax.set_ylabel("Avg Temperature (°F)")
        ax.grid(True, alpha=0.3)
        legend = ax.legend(loc='upper left', fontsize='small')

        # Clickable legend to toggle series visibility
        lined = {}
        try:
            leg_lines = legend.get_lines()
            for legline, origline in zip(leg_lines, lines):
                legline.set_picker(True)
                legline.set_pickradius(5)
                lined[legline] = origline

            def on_pick(event):
                legline = event.artist
                if legline in lined:
                    origline = lined[legline]
                    vis = not origline.get_visible()
                    origline.set_visible(vis)
                    legline.set_alpha(1.0 if vis else 0.3)
                    self.canvas.draw_idle()
            self.figure.canvas.mpl_connect('pick_event', on_pick)
        except Exception:
            pass

        # Hover tooltips on data lines
        if mplcursors and lines:
            try:
                cursor = mplcursors.cursor(lines, hover=True)
                @cursor.connect("add")
                def _on_add(sel):
                    x, y = sel.target
                    sel.annotation.set_text(f"Year: {int(round(x))}\nAvg: {y:.1f}°")
            except Exception:
                pass

        # Brushing (drag to zoom x-range), double-click to reset
        try:
            from matplotlib.widgets import SpanSelector
            def onselect(xmin, xmax):
                ax.set_xlim(xmin, xmax)
                self.canvas.draw_idle()
            span = SpanSelector(ax, onselect, 'horizontal', useblit=True, alpha=0.15, rectprops=dict(facecolor='gray', alpha=0.2))
            def on_dbl(event):
                if event.dblclick and event.inaxes == ax:
                    ax.relim(); ax.autoscale_view()
                    self.canvas.draw_idle()
            self.figure.canvas.mpl_connect('button_press_event', on_dbl)
        except Exception:
            pass

        self.canvas.draw()

    def _render_extreme_events(self, cities: List[Dict]) -> None:
        if not _import_matplotlib():
            return
        # Limit number of subplots for readability
        max_cities = 4
        if len(cities) > max_cities:
            cities = cities[:max_cities]
            self.helper_label.configure(text=f"Showing first {max_cities} cities (limit for readability).", bootstyle="warning")
        self._reset_canvas()

        n = len(cities)
        n = max(1, n)
        axes = []
        for i in range(n):
            ax = self.figure.add_subplot(n, 1, i + 1, sharex=axes[0] if axes else None)
            axes.append(ax)

        start = '2010-01-01'
        end = datetime.now().strftime('%Y-%m-%d')

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for idx, city in enumerate(cities):
                cursor.execute(
                    """
                    SELECT date, temperature_max, rain, wind_gusts_max, temperature_min
                    FROM historical_weather
                    WHERE city = ? AND state = ? AND date BETWEEN ? AND ?
                    """,
                    (city['city'], city['state'], start, end)
                )
                rows = cursor.fetchall()
                if not rows:
                    continue
                import pandas as pd
                from collections import defaultdict
                df = pd.DataFrame(rows)
                df.columns = [col[0] for col in cursor.description]
                df['date'] = pd.to_datetime(df['date'])
                df['year'] = df['date'].dt.year

                counts = {}
                if self.event_hot_var.get():
                    counts['Hot >100F'] = df[df['temperature_max'] > 100].groupby('year').size()
                if self.event_rain_var.get():
                    counts['Rain >1in'] = df[df['rain'] > 1].groupby('year').size()
                if self.event_wind_var.get():
                    counts['WindGust >30'] = df[df['wind_gusts_max'] > 30].groupby('year').size()
                if self.event_cold_var.get():
                    counts['Cold <32F'] = df[df['temperature_min'] < 32].groupby('year').size()

                # Combine into a DataFrame with all years
                if counts:
                    years = sorted(df['year'].unique())
                    plot_df = pd.DataFrame(index=years)
                    for name, s in counts.items():
                        plot_df[name] = s
                    plot_df = plot_df.fillna(0)
                else:
                    plot_df = pd.DataFrame(index=sorted(df['year'].unique()))

                ax = axes[idx]
                bottom = np.zeros(len(plot_df))
                colors = ['#E4572E', '#4C78A8', '#72B7B2', '#F1A208']
                series_to_bars = defaultdict(list)
                bar_artists = []
                for i, col in enumerate(plot_df.columns):
                    bars = ax.bar(plot_df.index, plot_df[col].values, bottom=bottom, label=col, color=colors[i % len(colors)], width=0.8)
                    bottom = bottom + plot_df[col].values
                    # Track bars for hover and toggling
                    for j, rect in enumerate(bars):
                        rect.set_gid((col, int(plot_df.index[j])))
                        series_to_bars[col].append(rect)
                        bar_artists.append(rect)
                ax.set_ylabel(city['display_name'])
                ax.grid(True, axis='y', alpha=0.3)

                # Hover tooltips for bars
                if mplcursors and bar_artists:
                    try:
                        cursor = mplcursors.cursor(bar_artists, hover=True)
                        @cursor.connect("add")
                        def _on_add(sel):
                            series, year = sel.artist.get_gid()
                            val = sel.artist.get_height()
                            sel.annotation.set_text(f"{series}\n{year}: {int(val)} days")
                    except Exception:
                        pass

        # Build clickable legend on first axes to toggle series across subplots
        try:
            first_ax = axes[0]
            # Determine series labels from last plot_df in loop above; fallback to common set
            labels = []
            for h in first_ax.containers:
                if h.get_label() not in labels and not h.get_label().startswith("_"):
                    labels.append(h.get_label())
            if not labels:
                labels = ['Hot >100F', 'Rain >1in', 'WindGust >30', 'Cold <32F']
            handles = [plt.Rectangle((0, 0), 1, 1, color=['#E4572E', '#4C78A8', '#72B7B2', '#F1A208'][i % 4]) for i, _ in enumerate(labels)]
            legend = first_ax.legend(handles, labels, loc='upper left', ncol=2, fontsize='x-small')
            legend_map = {h: lbl for h, lbl in zip(legend.legendHandles, labels)}
            for h in legend.legendHandles:
                h.set_picker(True)
                h.set_pickradius(5)

            def on_pick(event):
                handle = event.artist
                label = legend_map.get(handle)
                if not label:
                    return
                # Toggle visibility of all rectangles with matching label across axes
                new_vis = None
                for ax in axes:
                    for cont in ax.containers:
                        if cont.get_label() == label:
                            for rect in cont:
                                new_vis = (not rect.get_visible()) if new_vis is None else new_vis
                                rect.set_visible(new_vis)
                handle.set_alpha(1.0 if (new_vis is None or new_vis) else 0.3)
                self.canvas.draw_idle()
            self.figure.canvas.mpl_connect('pick_event', on_pick)
        except Exception:
            pass

        axes[-1].set_xlabel("Year")
        self.figure.suptitle("Extreme Weather Frequency (stacked per city)")
        self.figure.tight_layout(rect=[0, 0.02, 1, 0.96])
        self.canvas.draw()

    def _render_monthly_deviation(self, cities: List[Dict]) -> None:
        if not _import_matplotlib():
            return
        import pandas as pd
        self._reset_canvas()
        max_cities = 4
        if len(cities) > max_cities:
            cities = cities[:max_cities]
            self.helper_label.configure(text=f"Showing first {max_cities} cities (limit for readability).", bootstyle="warning")

        n = len(cities)
        cols = 2 if n > 1 else 1
        rows = int(np.ceil(n / cols))
        axes = []
        for i in range(n):
            r = i // cols
            c = i % cols
            ax = self.figure.add_subplot(rows, cols, i + 1)
            axes.append(ax)

        start = '2010-01-01'
        end = datetime.now().strftime('%Y-%m-%d')

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            for idx, city in enumerate(cities):
                cursor.execute(
                    """
                    SELECT date, temperature_mean
                    FROM historical_weather
                    WHERE city = ? AND state = ? AND date BETWEEN ? AND ?
                    """,
                    (city['city'], city['state'], start, end)
                )
                rows = cursor.fetchall()
                if not rows:
                    continue
                df = pd.DataFrame(rows)
                df.columns = [col[0] for col in cursor.description]
                df['date'] = pd.to_datetime(df['date'])
                df = df.dropna(subset=['temperature_mean'])
                df['year'] = df['date'].dt.year
                df['month'] = df['date'].dt.month
                baseline = df.groupby('month')['temperature_mean'].mean()
                monthly_avg = df.groupby(['year', 'month'])['temperature_mean'].mean().unstack()
                deviation = monthly_avg.subtract(baseline, axis=1)
                ax = axes[idx]
                mesh = sns.heatmap(
                    deviation,
                    cmap="coolwarm",
                    center=0,
                    cbar_kws={'label': 'Δ from Monthly Avg (°F)'},
                    ax=ax,
                    linewidths=0.2,
                    linecolor='gray'
                )
                ax.set_title(city['display_name'])
                ax.set_xlabel("Month")
                ax.set_ylabel("Year")
                ax.set_xticks([i + 0.5 for i in range(12)])
                ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], rotation=45)

                # Hover tooltips for heatmap cells
                if mplcursors:
                    try:
                        cursor = mplcursors.cursor(ax.collections[0], hover=True)
                        @cursor.connect("add")
                        def _on_add(sel, d=deviation):
                            # sel.index expected to be (row, col)
                            try:
                                i, j = sel.index
                                year = int(d.index[i])
                                month_idx = int(d.columns[j])
                                month_name = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][month_idx - 1]
                                val = d.iloc[i, j]
                                sel.annotation.set_text(f"{month_name} {year}\nΔ {val:.1f}°")
                            except Exception:
                                pass
                    except Exception:
                        pass

        self.figure.suptitle("Monthly Deviation from Long-Term Avg")
        self.figure.tight_layout(rect=[0, 0.02, 1, 0.96])
        self.canvas.draw()