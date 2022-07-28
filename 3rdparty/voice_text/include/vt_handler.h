#ifndef VT_HANDLER_H_
#define VT_HANDLER_H_

#include <dlfcn.h>
#include <glob.h>
#include <string>

// logging
#include <ros/ros.h>

// Voice Text API and ReadSpeaker APi
#include <vt_jpn.h>
#include <vtapi.h>

#define VT_ROOT "/usr/vt/*/*"

#if __x86_64__ || __ppc64__
#define ENV64
#else
#define ENV32
#endif

typedef enum VT_TYPE{
NO_VT,
VT_SDK,
VT_API
} VT_Types;

class VTHandler{
public:
    VTHandler(std::string license_path);
    ~VTHandler();
    void VTH_TextToFile(int pitch, int speed, int volume, int pause,
                        char* text_char, char* wave_path);
    void VTH_Exit();
private:
    void* dl_handle;
    VT_Types vt_type;
};


#endif // VT_HANDLER_H_
