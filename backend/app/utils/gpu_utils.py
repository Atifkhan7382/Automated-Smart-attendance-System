"""
GPU Utilities for Face Recognition
Handles GPU detection and optimization
"""

import os
import cv2
import numpy as np
from typing import Optional, Dict, Any
import logging

class GPUManager:
    def __init__(self, skip_detailed_info=True):
        self.gpu_available = False
        self.cuda_available = False
        self.opencl_available = False
        self.device_info = {}
        self.skip_detailed_info = skip_detailed_info
        self._detect_gpu_capabilities()
    
    def _detect_gpu_capabilities(self):
        """Detect available GPU capabilities (fast mode)"""
        try:
            # Quick CUDA check
            try:
                if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                    self.cuda_available = True
                    self.gpu_available = True
                    self.device_info['cuda_devices'] = cv2.cuda.getCudaEnabledDeviceCount()
            except:
                pass
            
            # Quick OpenCL check (skip slow operations)
            try:
                if cv2.ocl.haveOpenCL():
                    self.opencl_available = True
                    self.gpu_available = True
                    cv2.ocl.setUseOpenCL(True)
            except:
                pass
            
            # Only get detailed info if explicitly requested
            if not self.skip_detailed_info:
                self._get_device_info()
            
        except Exception as e:
            # Silently fail for faster startup
            self.gpu_available = False
    
    def _get_device_info(self):
        """Get detailed GPU device information (slow operation)"""
        try:
            if self.cuda_available:
                try:
                    device = cv2.cuda.getDevice()
                    self.device_info.update({
                        'current_cuda_device': device,
                        'cuda_arch_bin': cv2.cuda.DeviceInfo().majorVersion(),
                        'cuda_arch_ptx': cv2.cuda.DeviceInfo().minorVersion()
                    })
                except:
                    pass
            
            if self.opencl_available:
                try:
                    # Skip this slow operation - it causes startup delays
                    # context = cv2.ocl.Context_create()
                    # if context.ndevices() > 0:
                    #     device = context.device(0)
                    #     self.device_info.update({
                    #         'opencl_device_name': device.name(),
                    #         'opencl_device_type': device.type(),
                    #         'opencl_max_compute_units': device.maxComputeUnits()
                    #     })
                    self.device_info['opencl_enabled'] = True
                except:
                    pass
        except Exception as e:
            pass  # Silently ignore errors
    
    def optimize_opencv_for_gpu(self):
        """Optimize OpenCV settings for GPU usage"""
        try:
            if self.cuda_available:
                try:
                    cv2.cuda.setDevice(0)
                except:
                    pass
            
            if self.opencl_available:
                try:
                    cv2.ocl.setUseOpenCL(True)
                except:
                    pass
            
            # Set number of threads for CPU operations
            cv2.setNumThreads(0)  # Use all available cores
            
            # Enable optimized code paths
            cv2.setUseOptimized(True)
            
        except Exception as e:
            pass  # Silently ignore errors
    
    def create_gpu_mat(self, image: np.ndarray) -> Any:
        """Create GPU matrix from numpy array"""
        if self.cuda_available:
            try:
                gpu_mat = cv2.cuda_GpuMat()
                gpu_mat.upload(image)
                return gpu_mat
            except Exception as e:
                print(f"GPU mat creation error: {e}")
                return image
        return image
    
    def download_from_gpu(self, gpu_mat: Any) -> np.ndarray:
        """Download image from GPU memory"""
        if self.cuda_available and hasattr(gpu_mat, 'download'):
            try:
                result = gpu_mat.download()
                return result
            except Exception as e:
                print(f"GPU download error: {e}")
                return gpu_mat
        return gpu_mat
    
    def get_status(self) -> Dict[str, Any]:
        """Get GPU status information"""
        return {
            'gpu_available': self.gpu_available,
            'cuda_available': self.cuda_available,
            'opencl_available': self.opencl_available,
            'device_info': self.device_info,
            'opencv_cuda_enabled': cv2.cuda.getCudaEnabledDeviceCount() > 0,
            'opencv_opencl_enabled': cv2.ocl.haveOpenCL()
        }

# Global GPU manager instance
gpu_manager = GPUManager()
