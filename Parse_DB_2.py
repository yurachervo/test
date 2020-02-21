import subprocess
import sqlite3
import os
import shutil
import datetime
import sys

datetime = datetime.datetime.now()
prefix = datetime.strftime('%y-%m-%d-%H-%M')


def connect_to_db(db_name):
    # Function connect to all found DBs and takes needed values 
    conn = sqlite3.connect(db_name, timeout=10)
    c = conn.cursor()
    c.execute("SELECT Data FROM axRepositoryOption WHERE Name='sourceserver_gitdir' OR Name='branch' OR Name='binary';")
    select1 = c.fetchall()
    b = conn.cursor()
    b.execute("SELECT Data FROM axMetaData WHERE Name='projectname';")
    select2 = b.fetchall()
    conn.close()
    db_info_list.append(db_name)
    for row1 in select1:
        db_info_list.append(str(u",".join(row1)))
    for row2 in select2:
        db_info_list.append(str(u",".join(row2)))
    return db_info_list


def match_branch( db_info_list, base_file_name):
    # Function print database info and records files which will be moved
    try:
        is_bare_repo = subprocess.check_output(['git', '--git-dir={}'.format(db_info_list[2]), 'rev-parse',
                                                '--is-bare-repository', db_info_list[2]]).strip()
        if "true" in is_bare_repo:
            os.chdir(db_info_list[2])
            branch = db_info_list[3]
            match_branch = subprocess.check_output(['git', 'branch', '--list', branch]).strip()
            if match_branch.replace('* ', '') == db_info_list[3]:
                print("==================== Database info =========================")
                print("Datbase name:     " + db_info_list[0])
                print("Project Name:     " + db_info_list[4])
                print("SCM:              " + db_info_list[1])
                print("Path to repo:     " + db_info_list[2])
                print("Branch:           " + db_info_list[3] + "                    the branch is matching with the "
                                                               "branch on bare repo")
                print("=============================================================")
            else:
                print("==================== Database info ==========================")
                print("Datbase name:     " + db_info_list[0] + "                    The database can be deleted")
                print("Project Name:     " + db_info_list[4])
                print("SCM:              " + db_info_list[1])
                print("Path to repo:     " + db_info_list[2])
                print("Branch:           " + db_info_list[3])
                print("=============================================================")
                move_db_files.append(base_file_name)
    except:
        print(db_info_list[0] + "    Bare repo for DB not exist or DB doesn't have needed parameters   ")
        error_db_files.append(db_info_list[0])
    os.chdir(r'C:\axivion_dashboard')


def uninstalled_projects(move_db_files):
    # Function restart Axivion and deletes projects from Axivion DB
    # ===========================================================
    cmd1 = r"cd C:\Program Files (x86)\Bauhaus\bin"
    cmd2 = "net stop axivion_dashboard_service"
    cmd3 = "net start axivion_dashboard_service"
    # ================= Create backup Axivion DB ========================
    shutil.copy(r'C:\axivion_dashboard_config\dashboard2.db', backup_folder)
    subprocess.call(cmd1, stdout=subprocess.PIPE, shell=True)
    process_stop = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    code = process_stop.wait()
    if code == 0:
        print("Axivion was stoped !")
        # =============== Connect to  Axivion DB =============================
        conn = sqlite3.connect(r'C:\axivion_dashboard_config\dashboard2.db', timeout=10)
        c = conn.cursor()
        for path_proj in move_db_files:
            path_proj_db = ("C:\\axivion_dashboard\\" + path_proj + ".db").replace('/', '\\')
            c.execute("DELETE FROM axProject WHERE Path='" + path_proj_db + "';")
        conn.commit()
        conn.close()
        process_start = subprocess.Popen(cmd3, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        code2 = process_start.wait()
        if code2 == 0:
            print("Axivion was restarted successfully  !")
    else:
        print("Error in Axivion restart!")


move_db_files = []
error_db_files = []
for root, dirs, files in os.walk("C:/axivion_dashboard/databases"):
    # Finding Databases files
    for file in files:
        db_info_list = []
        if file.endswith(".db"):
            db_name = os.path.join(root, file).replace('/', '\\')
            connect_to_db(db_name)
            base_file_name = (root + "/" + os.path.splitext(file)[0])  # .replace('\\', '/')
            match_branch(db_info_list, base_file_name)

if len(move_db_files) >= 1:
    # Create backup DBs with folders structure and files with deleted and false DBs
    if not os.path.exists(r"C:\axivion_dashboard\cleaning_db"):
        os.makedirs("cleaning_db" + '(' + prefix + ')')
    backup_folder = "cleaning_db" + '(' + prefix + ')'
    with open(backup_folder + "\\" + 'error_db_files.txt', 'w') as f:
        for item in error_db_files:
            f.write("%s\n" % item)
    with open(backup_folder + "\\" + 'move_db_files.txt', 'w') as f:
        for item in move_db_files:
            f.write("%s\n" % item)
    for file_ in move_db_files:
        all_db_files = os.path.basename(os.path.normpath(file_))
        path_to_file = os.path.dirname(file_)
        dst_dir = backup_folder + "\\" + file_
        dst_folder = os.path.dirname(dst_dir)
        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)
        for fname in os.listdir(path_to_file):
            if fname.startswith(all_db_files):
                shutil.move(path_to_file + "\\" + fname, dst_folder)

    uninstalled_projects(move_db_files)
else:
    print("Any DataBases for deleting weren't found")