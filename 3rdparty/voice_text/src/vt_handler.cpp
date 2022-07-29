/*
 * vt_handler.cpp
 * Author: Yoshiki Obinata <obinata@jsk.imi.i.u-tokyo.ac.jp>
 */

#include "vt_handler.h"

VTHandler::VTHandler(std::string lincense_path){
  glob_t sdk_old_gbuf_, sdk_new_gbuf_, api_gbuf_;
  std::string lib_file_;
#ifdef ENV64
  glob((VT_ROOT + "/bin/x86_64/RAMIO/libvt_jpn.so").c_str(), 0, NULL, &sdk_old_gbuf_); // e.g., /usr/vt/sayaka/M16/bin/x86_64/RAMIO/libvt_jpn.so
  glob((VT_ROOT + "/bin/LINUX64_GLIBC3/RAMIO/libvt_jpn.so").c_str(), 0, NULL, &sdk_new_gbuf_); // e.g., /usr/vt/risa/H16/bin/LINUX64_GLIBC3/RAMIO/libvt_jpn.so
  glob((VT_ROOT + "/bin/FILEIO/LINUX64_GLIBC3/libvt_jpn.so").c_str(), 0, NULL, &api_gbuf_); // e.g., /usr/vt/hikari/D16/bin/FILEIO/LINUX64_GLIBC3/libvt_jpn.so
#elif ENV32
  glob((VT_ROOT + "/bin/x86_32/RAMIO/libvt_jpn.so").c_str(), 0, NULL, &sdk_old_gbuf_); // e.g., /usr/vt/sayaka/M16/bin/x86_32/RAMIO/libvt_jpn.so
  glob((VT_ROOT + "/bin/LINUX32_GLIBC3/RAMIO/libvt_jpn.so").c_str(), 0, NULL, &sdk_new_gbuf_); // e.g., /usr/vt/risa/H16/bin/LINUX32_GLIBC3/RAMIO/libvt_jpn.so
  glob((VT_ROOT + "/bin/FILEIO/LINUX32_GLIBC3/libvt_jpn.so").c_str(), 0, NULL, &api_gbuf_); // e.g., /usr/vt/hikari/D16/bin/FILEIO/LINUX32_GLIBC3/libvt_jpn.so
#endif
  if(sdk_old_gbuf_.gl_pathc > 0){
    this->vt_type = VT_SDK;
    lib_file_ = sdk_old_gbuf_.gl_pathv[0];
  }else if(sdk_new_gbuf_.gl_pathc > 0){
    this->vt_type = VT_SDK;
    lib_file_ = sdk_new_gbuf_.gl_pathv[0];
  }else if(api_gbuf_.gl_pathc > 0){
    this->vt_type = VT_API;
    lib_file_ = api_gbuf_.gl_pathv[0];
  }else{
    this->vt_type = NO_VT;
  }

  globfree(&sdk_old_gbuf_);
  globfree(&sdk_new_gbuf_);
  globfree(&api_gbuf_);

  if(this->vt_type != NO_VT){
    this->dl_handle = dlopen(lib_file_, RTLD_NOW);
    LoadSym();
  }else{
    ROS_FATAL("No Voice Text or Read Speaker libraries have found\n");
    return;
  }
}

VTHandler::~VTHandler(){
  dlclose(this->dl_handle);
}

int VTHandler::LoadSym(){
  const char* dl_err_;
  if(vt_type == VT_SDK){
    s_VT_LOADTTS_JPN_ = dlsym(this->dl_handle, "VT_LOADTTS_JPN");
    s_VT_UNLOADTTS_JPN_ = dlsym(this->dl_handle, "VT_UNLOADTTS_JPN");
    s_VT_GetTTSInfo_JPN_ = dlsym(this->dl_handle, "VT_GetTTSInfo_JPN");
    s_VT_TextToFile_JPN_ = dlsym(this->dl_handle, "VT_TextToFile_JPN");
  }else if(vt_type == VT_API){

  }
  dl_err_ = dlerror();
  if (dl_err_ != NULL){
    ROS_FATAL_STREAM("Error occured when loading VoiceText or ReadSpeaker libraries"
                     << dl_err_);
    dlclose(this->dl_handle);
    return 1;
  }else{
    return 0;
  }
}

void VTHandler::VTH_TextToFile(int pitch, int speed, int volume, int pause,
                               char *text_char, char *wave_path){
}
