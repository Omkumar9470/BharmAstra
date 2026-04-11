export default function Header() {
  return (
    <header className="border-b border-border bg-background">
      <div className="mx-auto max-w-7xl px-4 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent">
              <span className="text-lg font-bold text-accent-foreground">₹</span>
            </div>
            <h1 className="text-2xl font-bold text-foreground">BharmAstra</h1>
          </div>
          <p className="text-sm text-muted-foreground">AI-Powered Indian Stock Predictor</p>
        </div>
      </div>
    </header>
  );
}
