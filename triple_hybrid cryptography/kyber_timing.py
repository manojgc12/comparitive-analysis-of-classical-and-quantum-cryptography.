import time
import statistics
from oqs import KeyEncapsulation

def measure_kyber_key_generation(algorithm="Kyber512", iterations=100):
    """
    Measure the time taken for Kyber key generation
    
    Args:
        algorithm: Kyber variant (Kyber512, Kyber768, Kyber1024)
        iterations: Number of iterations to run for statistical accuracy
    
    Returns:
        Dictionary containing timing statistics
    """
    print(f"\n=== Measuring {algorithm} Key Generation Time ===")
    print(f"Running {iterations} iterations...\n")
    
    try:
        times = []
        
        for i in range(iterations):
            # Create new KEM instance for each iteration
            kem = KeyEncapsulation(algorithm)
            
            # Measure key generation time
            start_time = time.perf_counter()
            public_key, secret_key = kem.generate_keypair()
            end_time = time.perf_counter()
            
            generation_time = (end_time - start_time) * 1000  # Convert to milliseconds
            times.append(generation_time)
            
            if (i + 1) % 20 == 0:
                print(f"Completed {i + 1}/{iterations} iterations...")
        
        # Calculate statistics
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        median_time = statistics.median(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0
        
        # Display results
        print(f"\n{algorithm} Key Generation Results:")
        print(f"{'='*50}")
        print(f"Average time:     {avg_time:.4f} ms")
        print(f"Minimum time:     {min_time:.4f} ms")
        print(f"Maximum time:     {max_time:.4f} ms")
        print(f"Median time:      {median_time:.4f} ms")
        print(f"Standard dev:     {std_dev:.4f} ms")
        print(f"Total iterations: {iterations}")
        
        return {
            'algorithm': algorithm,
            'avg_time_ms': avg_time,
            'min_time_ms': min_time,
            'max_time_ms': max_time,
            'median_time_ms': median_time,
            'std_dev_ms': std_dev,
            'iterations': iterations,
            'all_times': times
        }
        
    except Exception as e:
        print(f"Error measuring {algorithm}: {e}")
        return None

def compare_kyber_variants(iterations=50):
    """
    Compare key generation times across different Kyber variants
    """
    variants = ["Kyber512", "Kyber768", "Kyber1024"]
    results = {}
    
    print("\n" + "="*70)
    print("KYBER ALGORITHM KEY GENERATION TIMING COMPARISON")
    print("="*70)
    
    for variant in variants:
        result = measure_kyber_key_generation(variant, iterations)
        if result:
            results[variant] = result
            time.sleep(0.5)  # Brief pause between variants
    
    # Summary comparison
    if results:
        print(f"\n{'='*70}")
        print("SUMMARY COMPARISON")
        print(f"{'='*70}")
        print(f"{'Algorithm':<12} {'Avg Time (ms)':<15} {'Min Time (ms)':<15} {'Max Time (ms)':<15}")
        print("-" * 70)
        
        for variant, data in results.items():
            print(f"{variant:<12} {data['avg_time_ms']:<15.4f} {data['min_time_ms']:<15.4f} {data['max_time_ms']:<15.4f}")
    
    return results

def detailed_kyber_analysis(algorithm="Kyber768", iterations=200):
    """
    Perform detailed analysis of a specific Kyber variant
    """
    print(f"\n{'='*60}")
    print(f"DETAILED ANALYSIS: {algorithm}")
    print(f"{'='*60}")
    
    result = measure_kyber_key_generation(algorithm, iterations)
    
    if result:
        times = result['all_times']
        
        # Additional analysis
        print(f"\nDetailed Statistics:")
        print(f"{'='*40}")
        print(f"25th Percentile:  {statistics.quantiles(times, n=4)[0]:.4f} ms")
        print(f"75th Percentile:  {statistics.quantiles(times, n=4)[2]:.4f} ms")
        print(f"95th Percentile:  {statistics.quantiles(times, n=20)[18]:.4f} ms")
        print(f"99th Percentile:  {statistics.quantiles(times, n=100)[98]:.4f} ms")
        
        # Performance categorization
        fast_count = sum(1 for t in times if t < result['avg_time_ms'] * 0.8)
        slow_count = sum(1 for t in times if t > result['avg_time_ms'] * 1.2)
        normal_count = iterations - fast_count - slow_count
        
        print(f"\nPerformance Distribution:")
        print(f"{'='*40}")
        print(f"Fast operations (<80% avg):   {fast_count} ({fast_count/iterations*100:.1f}%)")
        print(f"Normal operations:            {normal_count} ({normal_count/iterations*100:.1f}%)")
        print(f"Slow operations (>120% avg):  {slow_count} ({slow_count/iterations*100:.1f}%)")
    
    return result

if __name__ == "__main__":
    print("KYBER ALGORITHM KEY GENERATION TIMING ANALYSIS")
    print("=" * 70)
    
    try:
        # Single algorithm detailed analysis
        print("\n1. Detailed Analysis of Kyber768:")
        detailed_result = detailed_kyber_analysis("Kyber768", 100)
        
        # Compare all variants
        print("\n\n2. Comparison of All Kyber Variants:")
        comparison_results = compare_kyber_variants(50)
        
        # Focus on fastest variant for additional testing
        if comparison_results:
            fastest_variant = min(comparison_results.keys(), 
                                key=lambda x: comparison_results[x]['avg_time_ms'])
            print(f"\n\n3. Extended Testing of Fastest Variant ({fastest_variant}):")
            extended_result = measure_kyber_key_generation(fastest_variant, 200)
        
    except ImportError:
        print("\nError: 'oqs' library not found!")
        print("Please install it using: pip install python-oqs")
    except Exception as e:
        print(f"Error running timing analysis: {e}")
