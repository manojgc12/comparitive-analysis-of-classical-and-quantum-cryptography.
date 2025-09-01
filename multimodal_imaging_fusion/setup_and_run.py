#!/usr/bin/env python3
"""
Quick setup and demo for Multimodal Imaging Fusion
This script creates a minimal working version and runs a demo
"""

import os
import sys
import subprocess
import numpy as np
import matplotlib.pyplot as plt

def print_header():
    print("=" * 60)
    print("  MULTIMODAL IMAGING FUSION - QUICK DEMO")
    print("=" * 60)
    print()

def check_imports():
    """Check if required packages are available"""
    print("Checking required packages...")
    
    required = ['numpy', 'matplotlib', 'torch']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✓ {pkg}")
        except ImportError:
            print(f"✗ {pkg} - MISSING")
            missing.append(pkg)
    
    if missing:
        print(f"\nMissing packages: {missing}")
        print("Installing via pip...")
        try:
            for pkg in missing:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            print("✓ Packages installed successfully")
        except:
            print("✗ Failed to install packages. Please install manually:")
            print(f"pip install {' '.join(missing)}")
            return False
    
    return True

def create_synthetic_data(size=(64, 64, 32)):
    """Create simple synthetic CT and MRI data"""
    print(f"Creating synthetic medical imaging data (size: {size})...")
    
    # Create base images with different characteristics
    ct_image = np.random.normal(0.3, 0.1, size).astype(np.float32)
    mri_image = np.random.normal(0.4, 0.15, size).astype(np.float32)
    
    # Add some synthetic "lesions"
    num_lesions = 3
    for i in range(num_lesions):
        # Random lesion location and size
        center_x = np.random.randint(10, size[0]-10)
        center_y = np.random.randint(10, size[1]-10) 
        center_z = np.random.randint(5, size[2]-5)
        radius = np.random.randint(3, 8)
        
        # Create spherical lesion
        x, y, z = np.ogrid[:size[0], :size[1], :size[2]]
        mask = (x - center_x)**2 + (y - center_y)**2 + (z - center_z)**2 <= radius**2
        
        # Modify intensities in lesion areas
        ct_image[mask] = np.random.uniform(0.7, 0.9)
        mri_image[mask] = np.random.uniform(0.6, 0.8)
    
    # Normalize to [0, 1]
    ct_image = np.clip(ct_image, 0, 1)
    mri_image = np.clip(mri_image, 0, 1)
    
    print("✓ Synthetic data created successfully")
    return ct_image, mri_image

def simple_fusion_demo(ct_image, mri_image):
    """Demonstrate simple fusion approaches"""
    print("Running fusion approaches demo...")
    
    # Simple fusion methods
    fusion_average = (ct_image + mri_image) / 2
    fusion_weighted = 0.6 * ct_image + 0.4 * mri_image
    fusion_max = np.maximum(ct_image, mri_image)
    fusion_difference = np.abs(ct_image - mri_image)
    
    print("✓ Fusion calculations completed")
    return fusion_average, fusion_weighted, fusion_max, fusion_difference

def visualize_results(ct_image, mri_image, fusions):
    """Create visualization of the fusion results"""
    print("Creating visualizations...")
    
    fusion_avg, fusion_weighted, fusion_max, fusion_diff = fusions
    
    # Select middle slice for visualization
    mid_slice = ct_image.shape[2] // 2
    
    # Create subplot
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('Multimodal Imaging Fusion Demo', fontsize=16, fontweight='bold')
    
    # Original images
    axes[0, 0].imshow(ct_image[:, :, mid_slice], cmap='gray')
    axes[0, 0].set_title('CT Image')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(mri_image[:, :, mid_slice], cmap='gray') 
    axes[0, 1].set_title('MRI Image')
    axes[0, 1].axis('off')
    
    axes[0, 2].imshow(fusion_diff[:, :, mid_slice], cmap='hot')
    axes[0, 2].set_title('CT-MRI Difference')
    axes[0, 2].axis('off')
    
    # Fusion results
    axes[1, 0].imshow(fusion_avg[:, :, mid_slice], cmap='gray')
    axes[1, 0].set_title('Average Fusion')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(fusion_weighted[:, :, mid_slice], cmap='gray')
    axes[1, 1].set_title('Weighted Fusion (0.6CT + 0.4MRI)')
    axes[1, 1].axis('off')
    
    axes[1, 2].imshow(fusion_max[:, :, mid_slice], cmap='gray')
    axes[1, 2].set_title('Maximum Fusion')
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    
    # Save the plot
    os.makedirs('results', exist_ok=True)
    plt.savefig('results/fusion_demo.png', dpi=300, bbox_inches='tight')
    print("✓ Visualization saved to 'results/fusion_demo.png'")
    
    # Show the plot
    plt.show()

def create_simple_model_demo():
    """Create a simple neural network fusion demo"""
    print("Creating simple neural network demo...")
    
    try:
        import torch
        import torch.nn as nn
        
        class SimpleFusionNet(nn.Module):
            def __init__(self):
                super().__init__()
                # Simple CNN for each modality
                self.ct_features = nn.Sequential(
                    nn.Conv2d(1, 16, 3, padding=1),
                    nn.ReLU(),
                    nn.AdaptiveAvgPool2d(1),
                    nn.Flatten(),
                    nn.Linear(16, 8)
                )
                
                self.mri_features = nn.Sequential(
                    nn.Conv2d(1, 16, 3, padding=1), 
                    nn.ReLU(),
                    nn.AdaptiveAvgPool2d(1),
                    nn.Flatten(),
                    nn.Linear(16, 8)
                )
                
                # Fusion classifier
                self.classifier = nn.Sequential(
                    nn.Linear(16, 8),
                    nn.ReLU(),
                    nn.Linear(8, 2)  # Binary classification
                )
            
            def forward(self, ct, mri):
                ct_feat = self.ct_features(ct)
                mri_feat = self.mri_features(mri) 
                fused = torch.cat([ct_feat, mri_feat], dim=1)
                return self.classifier(fused)
        
        # Create model
        model = SimpleFusionNet()
        total_params = sum(p.numel() for p in model.parameters())
        
        print(f"✓ Simple fusion neural network created with {total_params} parameters")
        
        # Test forward pass
        dummy_ct = torch.randn(2, 1, 32, 32)
        dummy_mri = torch.randn(2, 1, 32, 32)
        
        with torch.no_grad():
            output = model(dummy_ct, dummy_mri)
            print(f"✓ Forward pass test: input {dummy_ct.shape} -> output {output.shape}")
        
        return True
        
    except ImportError:
        print("⚠ PyTorch not available - skipping neural network demo")
        return False

def run_complete_demo():
    """Run the complete demonstration"""
    print_header()
    
    # Check requirements
    if not check_imports():
        print("❌ Cannot proceed without required packages")
        return False
    
    print("\n" + "="*40)
    print("RUNNING MULTIMODAL FUSION DEMO")
    print("="*40)
    
    # Generate synthetic data
    ct_img, mri_img = create_synthetic_data()
    
    # Run fusion demo
    fusions = simple_fusion_demo(ct_img, mri_img)
    
    # Create visualizations
    visualize_results(ct_img, mri_img, fusions)
    
    # Neural network demo
    create_simple_model_demo()
    
    print("\n" + "="*60)
    print("🎉 DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\n📊 Results:")
    print("  • Fusion visualization saved to: results/fusion_demo.png")
    print("  • Synthetic CT/MRI data generated and processed")
    print("  • Multiple fusion approaches demonstrated")
    print("  • Simple neural network model created")
    
    print("\n📈 What was demonstrated:")
    print("  1. Synthetic medical imaging data generation")
    print("  2. Basic image fusion techniques (averaging, weighting, maximum)")
    print("  3. Visual comparison of fusion results")
    print("  4. Simple CNN-based fusion architecture")
    
    print("\n🚀 Next steps:")
    print("  • Install full requirements: pip install -r requirements.txt")
    print("  • Run advanced fusion models with attention mechanisms")
    print("  • Try with real CT/MRI datasets")
    print("  • Experiment with different fusion approaches")
    
    return True

if __name__ == "__main__":
    success = run_complete_demo()
    if success:
        input("\nPress Enter to exit...")
    else:
        print("Demo failed. Check error messages above.")
        input("\nPress Enter to exit...")
