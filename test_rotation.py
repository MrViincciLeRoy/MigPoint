from adsterra_provider import AdsterraProvider

ap = AdsterraProvider()
formats = {}

print("Testing ad rotation (20 samples):\n")

for i in range(20):
    ad = ap.fetch_ad()
    fmt = ad.get('format')
    formats[fmt] = formats.get(fmt, 0) + 1
    print(f"  Ad {i+1}: {fmt}")

print("\n" + "="*40)
print("SUMMARY:")
print("="*40)

for fmt, count in sorted(formats.items()):
    pct = count * 5
    print(f"{fmt:20} {count:2} occurrences ({pct}%)")
